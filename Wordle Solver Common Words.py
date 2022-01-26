#!/usr/bin/env python
# coding: utf-8

# In[25]:


import numpy as np


# In[26]:


my_file = open("common_words.csv", "r",encoding='utf-8-sig')
#using Google's 10000 most common words ordered by frequency 
#https://github.com/first20hours/google-10000-english
#of those 10000 words, there are 1367 that are 5 letters
content = my_file.read()
five_letter_words = content.split("\n")


# In[27]:


def start():
    status = 0
    while status != 1:
        candidate = np.random.choice(five_letter_words)
        if sum([1 if (candidate[i] in ['a','e','i','o','u']) else 0 for i in range(5)])>=2 and sum([1 if (candidate[i] in ['r','s','t','l','n']) else 0 for i in range(5)])>=2 and len(set(candidate))==5:
            status = 1
        else:
            status = 0
    return candidate


# In[28]:


def green_check(candidate_word,green_list):
    if len(green_list) == 0:
        green_status = 1
    else:
        gclist = [candidate_word[p[1]] == p[0] for p in green_list]
        green_status = all(gclist)
    return green_status


# In[29]:


def yellow_check(candidate_word,yellow_list):
    if len(yellow_list) == 0:
        yellow_status = 1
    else:
        yclist = [(p[0] in candidate_word) and (candidate_word[p[1]] != p[0]) for p in yellow_list]
        yellow_status = all(yclist)
    return yellow_status


# In[30]:


def black_check(candidate_word,black_list):
    black_status = all([letter not in candidate_word for letter in black_list])
    return black_status


# In[31]:


def update_list(word_list,black_list,green_list,yellow_list):
    new_word_list = []
    for word in word_list:
        if all([green_check(word,green_list),yellow_check(word,yellow_list),black_check(word,black_list)]):
            new_word_list.append(word)
    return new_word_list


# In[32]:


new_word = start()
word_list = five_letter_words
print("Initial Guess:", new_word)
green_list = []
yellow_list = []
black_list = []
status = input("Wordle's Response: ")
while status != 'GGGGG':
    for i in range(len(status)):
        if status[i] == 'G':
            green_list.append([new_word[i],i])
        if status[i] == 'Y':
            yellow_list.append([new_word[i],i])
        if status[i] == '0':
            black_list.append(new_word[i])
    word_list = update_list(word_list,black_list,green_list,yellow_list)
    new_word = word_list[0]
    print("Next Guess:", new_word)
    status = input("Wordle's Response: ")


# In[ ]:




