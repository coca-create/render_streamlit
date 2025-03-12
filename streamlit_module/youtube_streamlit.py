import os
import re


# import spacy
from datetime import datetime
import tempfile
import zipfile
from streamlit_module import moz_sp as sp
from streamlit_module import moz_tab9 as t9
import streamlit as st
import csv

# Spacyの英語モデルをロード
#nlp = spacy.load("en_core_web_lg")


def parse_srt_file(srt_path):
    with open(srt_path, 'r', encoding='utf-8') as file:
        srt_text = file.read()
    #print(f"最初の読み込み:{srt_text}")
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\d|\Z)', re.S)
    matches = pattern.findall(srt_text)
    return matches

def to_seconds(time_str):
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def seconds_to_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    
    # ミリ秒を3桁に揃える
    milliseconds_str = f"{milliseconds:03}"
    
    # フォーマットはHH:MM:SS,SSSとする
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds_str}"

def calculate_word_timestamps(start_time, end_time, text):
    words = text.split()
    total_chars = sum(len(word) for word in words)
    start_seconds = to_seconds(start_time)
    end_seconds = to_seconds(end_time)
    duration = end_seconds - start_seconds

    word_timestamps = []
    elapsed_chars = 0

    for word in words:
        word_start = start_seconds + (elapsed_chars / total_chars) * duration
        elapsed_chars += len(word)
        word_end = start_seconds + (elapsed_chars / total_chars) * duration
        word_timestamps.append({
            "start": round(word_start, 3),
            "end": round(word_end, 3),
            "word": protect_special_cases(word)
        })

    return word_timestamps

def srt_to_word_timestamps(srt_path):
    segments = parse_srt_file(srt_path)
    all_word_timestamps = []

    for segment in segments:
        index, start_time, end_time, text = segment
        word_timestamps = calculate_word_timestamps(start_time, end_time, text)
        all_word_timestamps.extend(word_timestamps)

    return all_word_timestamps

def srt_to_plain_text(srt_path):
    segments = parse_srt_file(srt_path)
    plain_text = " ".join([segment[3].replace("\n", " ") for segment in segments])
    return plain_text

'''def add_punctuation(text):
    model_name = "oliverguhr/fullstop-punctuation-multilang-large"
    model = PunctuationModel(model=model_name)
    punctuated_text = model.restore_punctuation(text)
    
    # 文末の余計なピリオドを削除
    punctuated_text = re.sub(r'\.\.+', '.', punctuated_text)
    
    return punctuated_text'''

def add_punctuation(model,text):
    if not text.strip():
        st.error("空のテキストが渡されました。")
        return text
    

    #print(f"model:{model_name}")
  
    
    try:
        if len(text) > 0:
            punctuated_text = model.restore_punctuation(text)
            punctuated_text = re.sub(r'\.\.+', '.', punctuated_text)
        else:
            punctuated_text = text
            st.error("文章が空か、エラーが発生しています")
        return punctuated_text
    except IndexError as e:
        st.error(f"エラーが発生しました: {str(e)}")
        return text


def save_punctuated_text(punctuated_text, base_name):
    
    lines = punctuated_text.split('. ')
         
    timestamp_patch = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_dir = os.path.join(tempfile.gettempdir(), f"session_{st.session_state.user_id}",f"{timestamp_patch}")
    os.makedirs(temp_dir, exist_ok=True)
    yt_txt_path = os.path.join(temp_dir, f"{base_name}_ytp.txt")

    with open(yt_txt_path, "w", encoding="utf-8") as f:
        for line in lines:
            line = line.replace("[dot]",".")
            #line = capitalize_proper_nouns_and_sentences(line)  # Spacyで大文字化
            #line = fix_spacing_issues(line)  # スペースの問題を修正
            if not line.endswith('.'):
                line += '. '
            f.write(line)
    return yt_txt_path

def create_srt_segments(json_data, punctuated_text):
    srt_segments = []
    #print(f"create_srt_segments_json_data:{json_data}")
    #print(f"create_srt_segments_punctuated_text:{punctuated_text}")
    words = punctuated_text.split()
    #print(f"create_srt_segments(punctuated_text.split):{words}")
    current_segment = {
        "start": json_data[0]["start"],
        "end": None,
        "text": ""
    }
    search_window = 7
    i = 0

    while i < len(words):
        word = words[i]
        if '.' in word and i + 1 < len(words):
            search_end_index = min(i + 1, len(words))
            search_start_index = max(0, search_end_index - search_window)
            search_words_list = words[search_start_index:search_end_index]
            search_words = " ".join(search_words_list).lower().replace(",", "").replace(".", "").replace(" ", "").replace("?", "").replace(":", "").replace("-", "")
            
            #print(f"Debug: searching for '{search_words}' in json_data")

            json_search_window = len(search_words_list)
            for j in range(len(json_data) - json_search_window + 1):
                json_search_words = "".join([entry["word"].lower().replace(",", "").replace(".", "").replace(" ", "").replace("?", "").replace(":", "").replace("-", "") for entry in json_data[j:j + json_search_window]])
                
                #print(f"Debug: comparing with '{json_search_words}'")

                if search_words == json_search_words:
                    current_segment["end"] = json_data[j + json_search_window - 1]["end"]
                    current_segment["text"] = " ".join(words[:i + 1])
                    srt_segments.append(current_segment)
                    
                    words = words[i + 1:]
                    json_data = json_data[j + json_search_window:]
                    current_segment = {
                        "start": json_data[0]["start"],
                        "end": None,
                        "text": ""
                    }
                    i = -1
                    break
        i += 1

    current_segment["end"] = json_data[-1]["end"]
    current_segment["text"] = " ".join(words)
    srt_segments.append(current_segment)

    return srt_segments

def save_srt(srt_segments, base_name):
    timestamp_patch = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_dir = os.path.join(tempfile.gettempdir(), f"session_{st.session_state.user_id}",f"{timestamp_patch}")
    os.makedirs(temp_dir, exist_ok=True)
    yt_srt_path = os.path.join(temp_dir,f"{base_name}_ytp.srt")    
    with open(yt_srt_path, "w", encoding="utf-8") as f:
        if st.session_state.select_rp_result and st.session_state.replace_word:
     
            with open("replacements.csv", newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # ヘッダーをスキップ
                replacements = [(row[0], row[1]) for row in reader]
        


        for idx, segment in enumerate(srt_segments, 1):
            start_time = seconds_to_timestamp(segment["start"])
            end_time = seconds_to_timestamp(segment["end"])
            segment['text']=segment['text'].replace("[dot]",".")

            if st.session_state.select_rp_result and st.session_state.replace_word:
                for original, replacement in replacements:
                    original=re.escape(original)
                    new_original = rf"\b{original}\b"
                    segment['text'] = re.sub(new_original, replacement, segment['text'])

            text=segment['text']
            #text = capitalize_proper_nouns_and_sentences(segment['text'])  # Spacyで大文字化
            #text = fix_spacing_issues(text)  # スペースの問題を修正
            f.write(f"{idx}\n{start_time} --> {end_time}\n{text}\n\n")
    
    return yt_srt_path

def protect_special_cases(text):
    protected_text=t9.protect_special_cases_srt(text)
    return protected_text



# ファイル処理を行う関数
def process_files(nlp,model,uploaded_file_path,spinner_holder,replace_word=False):
    srt_path = uploaded_file_path
    #print(srt_path)
    
    base_name = os.path.splitext(os.path.basename(srt_path))[0]
    timestamp_patch = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_dir = os.path.join(tempfile.gettempdir(), f"session_{st.session_state.user_id}",f"{timestamp_patch}")
    os.makedirs(temp_dir, exist_ok=True)
    with spinner_holder:
        with st.spinner(" ピリオドを追加しています。"):
    
            plain_text = srt_to_plain_text(srt_path)
            #print(f"plain_text from srt_to_plain_text :{plain_text}")
            
            dot_protect_text = protect_special_cases(plain_text)
            #print(f"dot_protect_text{dot_protect_text}")
            punctuated_text = add_punctuation(model,dot_protect_text)
            dot_protect_text = protect_special_cases(punctuated_text)
            #output_name1 = f'{base_name}_ytp_NR.txt'
            #temp_yt_txt_path=save_punctuated_text(punctuated_text, base_name)
        with st.spinner(" capitalize処理を行っています。"):
            #yt_txt_pathNR,yt_txt_pathR=sp.process_text_file(nlp,temp_yt_txt_path,output_name1,replace_word)
            word_timestamps = srt_to_word_timestamps(srt_path)
            srt_segments = create_srt_segments(word_timestamps, punctuated_text)
            temp_yt_srt_path=save_srt(srt_segments, base_name)
            output_name2 = f'{base_name}_ytp.srt'
            yt_srt_path = sp.process_srt_file(nlp,temp_yt_srt_path,output_name2,None,replace_word)

            output_name3=f'{base_name}_ytp_NR.txt'
            output_name4=f'{base_name}_ytp_R.txt'
            yt_txt_pathNR=os.path.join(temp_dir,output_name3)
            yt_txt_pathR=os.path.join(temp_dir,output_name4)

            with open(yt_srt_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            # SRTのパターン: ID -> タイムスタンプ -> 字幕
            segments = re.split(r"\n\n", content.strip())
            cleaned_segments = []
            
            for segment in segments:
                lines = segment.split("\n")
                if len(lines) < 2:
                    continue
                
                # IDとタイムスタンプを削除（最初の2行）
                subtitle_text = "\n".join(lines[2:])
                cleaned_segments.append(subtitle_text)
            
            cleaned_text = "\n".join(cleaned_segments)
            cleaned_text2=" ".join(cleaned_segments)
            with open(yt_txt_pathR, "w", encoding="utf-8") as file:
                file.write(cleaned_text)
            with open(yt_txt_pathNR,"w",encoding="utf-8") as file2:
                file2.write(cleaned_text2)
            

    # 生成されたファイルのパスを返す
    return yt_srt_path, yt_txt_pathNR,yt_txt_pathR

