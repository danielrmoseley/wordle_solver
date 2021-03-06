#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 20:26:06 2022

@author: danielmoseley
"""

import nltk
nltk.download('words')
from nltk.corpus import words
import numpy as np
import streamlit as st

st.title('Wordle Solver')


five_letter_words = []
for word in words.words():
    if len(word)==5:
        five_letter_words.append(word.lower())
        


def start():
    return np.random.choice(five_letter_words)


def green_check(candidate_word,Greens):
    if len(Greens) == 0:
        green_status = 1
    else:
        gclist = [candidate_word[p[1]] == p[0] for p in Greens]
        green_status = all(gclist)
    return green_status



def yellow_check(candidate_word,Yellows):
    if len(Yellows) == 0:
        yellow_status = 1
    else:
        yclist = [p[0] in candidate_word for p in Yellows]
        yellow_status = all(yclist)
    return yellow_status



def black_check(candidate_word,black_list):
    black_status = all([letter not in candidate_word for letter in black_list])
    return black_status



def next_guess(response,new_word,black_list=[]):
    Greens = []
    Yellows = []
    status = [False,False,False]
    for i in range(len(response)):
        if response[i] == 'G':
            Greens.append([new_word[i],i])
        if response[i] == 'Y':
            Yellows.append([new_word[i],i])
    while status != [True,True,True]:
        candidate_word = np.random.choice(five_letter_words)
        status = [green_check(candidate_word,Greens),yellow_check(candidate_word,Yellows),black_check(candidate_word,black_list)]
    return candidate_word

if 'word' not in st.session_state:
    st.session_state['word'] = start()
    st.session_state['black_list'] = []
    st.session_state['status'] = 'aaaaa'

with st.form("my_form",clear_on_submit=True):
    new_word = st.session_state.word
    status = st.session_state.status
        
    st.write('Guess:', new_word)
    submitted = st.form_submit_button("Submit")
    
    col1,col2,col3,col4,col5 = st.columns(5)
    
    with col1:
        letter1 = st.radio( new_word[0].upper(),('grey', 'yellow', 'green'),key='letter1')
    
    with col2:
        letter2 = st.radio( new_word[1].upper(),('grey', 'yellow', 'green'),key='letter2')
    
    with col3:
        letter3 = st.radio( new_word[2].upper(),('grey', 'yellow', 'green'),key='letter3')
    
    with col4:
        letter4 = st.radio( new_word[3].upper(),('grey', 'yellow', 'green'),key='letter4')
    
    with col5:
        letter5 = st.radio( new_word[4].upper(),('grey', 'yellow', 'green'),key='letter5')


    # Every form must have a submit button.
    if submitted:
        colors = [letter1,letter2,letter3,letter4,letter5]
        status = ''.join(['0' if c=='grey' else 'Y' if c=='yellow' else 'G' for c in colors])
        st.session_state.status = status
        st.write(status)

        for j in range(5):
            if status[j]=='0':
                st.session_state.black_list.append(new_word[j])
        st.session_state.word = next_guess(status,new_word,st.session_state.black_list)
        st.experimental_rerun()

