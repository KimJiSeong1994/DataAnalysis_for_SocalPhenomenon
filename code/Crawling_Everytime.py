# =============================================== [ setting ] ==========================================================
import pandas as pd
import random
import time
from selenium import webdriver
driver = webdriver.Chrome("/Users/gimjiseong/Downloads/selenium/chromedriver")

id_list = [" "] # id
ps_list = [" "] # pw

# + todo [ Web login ] ====================
driver.get("https://everytime.kr/login")
input_ID = driver.find_element_by_xpath('//*[@id="container"]/form/p[1]/input')
input_ID.send_keys(id_list)
input_ps = driver.find_element_by_xpath('//*[@id="container"]/form/p[2]/input')
input_ps.send_keys(ps_list)
time.sleep(random.uniform(0, 1))

login = driver.find_element_by_css_selector('p.submit')
login.click()

try:
    more_information = driver.find_element_by_css_selector('a.more')
    more_information.click()
except:
    pass

link_url = driver.find_elements_by_css_selector('a.new')
links = [url.get_attribute('href') for url in link_url] # 게시판 링크
cage_name = [url.text for url in link_url] # 게시판 이름

univ_name = driver.find_element_by_xpath('//*[@id="logo"]/p/span[2]').text

# =============================================== [ Crwaling ] =========================================================
obs_id = 6814 + 2861 + 7939 + 11862 + 4074 + 2077 #164479 한양대
total_df = df = pd.DataFrame(columns = ["Univ", "Categories", "obs_id", "Date", "Title", "Content"])
for n in range(0, len(links)) :
    driver.get(links[n])
    time.sleep(random.uniform(2, 3))
    # + todo [ close popup ] =====================
    try:
        remove_adv = driver.find_element_by_xpath('//*[@id="sheet"]/ul/li[3]/a')  # 팜업창 닫기
        remove_adv.click()
    except:
        pass

    # + todo [ data gathering ] ===================
    for pg in range(500, 5000) : # 한양대 : 2102
        driver.get(links[n]+ "/p/" + str(pg))  # navigate web page
        time.sleep(random.uniform(2, 3))
        try:
            remove_adv = driver.find_element_by_xpath('//*[@id="sheet"]/ul/li[3]/a')
            remove_adv.click()
        except:
            pass

        article_link = driver.find_elements_by_css_selector('article > a.article')
        article_links = [url.get_attribute('href') for url in article_link]
        for url in article_links:
            driver.get(url)
            time.sleep(random.uniform(2, 3))
            obs_id += 1

            c_name = cage_name[n]
            o_date = driver.find_element_by_xpath('//*[@id="container"]/div[2]/article/a/div/time').text
            try :
                o_title = driver.find_element_by_css_selector('a.article > h2.large').text
            except :
                o_title = "nontitle"

            o_content = driver.find_element_by_xpath('//*[@id="container"]/div[2]/article/a/p').text
            df = pd.DataFrame({"Univ" : univ_name, "Categories" : c_name, "obs_id": obs_id, "Date": o_date, "Title": o_title, "Content": o_content}, index=[obs_id])
            try:
                p_contents = driver.find_elements_by_css_selector("article.parent > p.large")
                p_content = ["re : " + cont.text for cont in p_contents]

                l = [obs_id] * len(p_content)
                D = [o_date] * len(p_content)
                T = [o_title] * len(p_content)
                C = [c_name] * len(p_content)
                re_content = pd.DataFrame({"Univ" : univ_name, "Categories" : C, "obs_id": l, "Date": o_date, "Title": T, "Content": p_content})
                df = df.append(re_content)
                try:
                    c_contents = driver.find_elements_by_css_selector("article.child > p.large")
                    c_content = ["rere : " + cont.text for cont in c_contents]

                    C = [c_name] * len(p_content)
                    l = [obs_id] * len(c_content)
                    D = [o_date] * len(c_content)
                    T = [o_title] * len(c_content)
                    rere_content = pd.DataFrame({"Univ" : univ_name, "Categories" : C, "obs_id": l, "Date": o_date, "Title": T, "Content": c_content})
                    df = df.append(rere_content)
                except :
                    pass
            except :
                pass

            total_df = total_df.append(df)
            total_df = total_df.drop_duplicates()
            total_df.to_csv("everytime8.csv", encoding = "utf-8")
            print("cage : ", cage_name[n], "page : ", pg, "Obs. : ", total_df.shape[0])
