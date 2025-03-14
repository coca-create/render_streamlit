import streamlit as st
import os
import os
import warnings
import shutil
import warnings

from streamlit_module import common as co
import logging
import json

st.set_page_config(
    page_title="PeriOz 2",
    page_icon="	:maple_leaf:",
    layout="wide",
    initial_sidebar_state="expanded",)

logging.getLogger("tornado.access").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="transformers.pipelines.token_classification")
#co.expire()


script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 各ユーザーのAppDataフォルダのパス（PeriOz2フォルダ）

data_src_path = os.path.join(script_dir, 'Data')

# AppData\Roaming内にPeriOz2フォルダが存在しない場合は作成



#appdataフォルダのパスを再設定
import tempfile
import os
import shutil
import uuid

SETTINGS_FILE = "settings.json"




# 初回アクセス時にセッションIDを作成
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())  # ランダムなセッションID

temp_dir = os.path.join(tempfile.gettempdir(), f"session_{st.session_state.user_id}")
os.makedirs(temp_dir, exist_ok=True)

if 'setpath' not in st.session_state:
    st.session_state.setpath=os.path.join(temp_dir,"settings.json")

if not os.path.exists(st.session_state.setpath):
    shutil.copy(SETTINGS_FILE, st.session_state.setpath)


##ここから、ロード開始。
if 'language_result' not in st.session_state:
    st.session_state.language_result=co.initialize_load('language_result')

if 'language_key' not in st.session_state:
    st.session_state.language_key=st.session_state.language_result
if 'dot_input1' not in st.session_state:
    st.session_state['dot_input1'] = None
if 'dot_input2' not in st.session_state:
    st.session_state['dot_input2'] = None
if 'rp_input1' not in st.session_state:
    st.session_state['rp_input1'] = None
if 'rp_input2' not in st.session_state:
    st.session_state['rp_input2'] = None
if 'rp_input3' not in st.session_state:
    st.session_state['rp_input3'] = None

if 'rp_key' not in st.session_state:
    st.session_state.rp_key=co.initialize_load_rp()

if 'dammy_rp_key' not in st.session_state:
    st.session_state.dammy_rp_key=co.initialize_load_rp()    

if 'select_rp_result' not in st.session_state:
    st.session_state.select_rp_result=co.initialize_load_rp()
    
if 'dot_key' not in st.session_state:
    st.session_state.dot_key=co.initialize_load_dot()

if 'select_dot_result' not in st.session_state:
    st.session_state.select_dot_result=co.initialize_load_dot()
    #if st.session_state.select_dot_result:
        #print('st.session_state.select_dot_result is loaded')

if 'dammy_dot_key' not in st.session_state:
    st.session_state.dammy_dot_key=co.initialize_load_dot()

if 'toggle_key' not in st.session_state:
    st.session_state.toggle_key = co.initialize_load('replace_words')

if 'replace_word' not in st.session_state:
    st.session_state.replace_word = co.initialize_load('replace_words') 

if 'ja_split' not in st.session_state:
    st.session_state.ja_split=co.initialize_load('ja_split')

if 'ja_split_key' not in st.session_state:
    st.session_state.ja_split_key=co.initialize_load('ja_split')

if 'comma_split' not in st.session_state:
    st.session_state.comma_split=co.initialize_load('comma_split')

if 'comma_split_key' not in st.session_state:
    st.session_state.comma_split_key=co.initialize_load('comma_split')

if 'min_split' not in st.session_state:
    st.session_state.min_split=co.initialize_load('min_split')

if 'min_split_current' not in st.session_state:
    st.session_state.min_split_current=st.session_state.min_split

if 'max_split' not in st.session_state:
    st.session_state.max_split=co.initialize_load('max_split')

if 'max_split_current' not in st.session_state:
    st.session_state.max_split_current=st.session_state.max_split

if 'model_option_key' not in st.session_state:
    st.session_state.model_option_key=co.initialize_load("model_option")

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = co.initialize_load("model_option")

if 'model_option_key2' not in st.session_state:
    st.session_state.model_option_key2=co.initialize_load("model_option2")

if 'selected_model2' not in st.session_state:
    st.session_state.selected_model2 = co.initialize_load("model_option2")

if 'model_option_key3' not in st.session_state:
    st.session_state.model_option_key3=co.initialize_load("model_option3")

if 'selected_model3' not in st.session_state:
    st.session_state.selected_model3 = co.initialize_load("model_option3")

if 'deepall' not in st.session_state:
    st.session_state.deepall=co.initialize_load("deepall")

if 'deepall_key' not in st.session_state:
    st.session_state.deepall_key=co.initialize_load("deepall")

if 'base_model' not in st.session_state:
    st.session_state.base_model=None

if 'large_model' not in st.session_state:
    st.session_state.large_model=None

if 'spacy_model' not in st.session_state:
    st.session_state.spacy_model=None

co.load_multi()

co.main()
