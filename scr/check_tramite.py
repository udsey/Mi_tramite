from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import time
import pandas as pd
import re

def check_status(driver, key, impl_wait=30):
    try:
        input_field = driver.find_element(By.ID, 'tramite').send_keys(key)
        time.sleep(random.random() + 2)
        botton = driver.find_element(By.ID, 'btn-consultar').click()
        driver.implicitly_wait(impl_wait)
        status = driver.find_element(By.CLASS_NAME, 'descripcion-estado').text
        time.sleep(random.random() + 1)
        return status
    
    except Exception as e:
        print(e)
        status = 'Error'
    finally:
        return status

def check_tramites(path, headless=True, impl_wait=30):
    
    flag = 0
    message = 'No updates'
    keys_df = pd.read_csv(path + 'data/id_data.csv')
    
    # Browser settings
    options = webdriver.ChromeOptions()
    
    if  headless:
        options.add_argument("headless")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get('https://mitramite.renaper.gob.ar/')
        driver.implicitly_wait(impl_wait)
        time.sleep(random.random() + 1.5)
        
        # Loop to check all ID's status in file
        for i, row in keys_df.iterrows():
            
            name, key, status = row
            new_status = check_status(driver, key)
            
            if new_status == 'Error':
                message = 'Update error'
                  
            elif new_status != status:
                print('Status was updated')
                
                if flag == 1:
                   message += "{}'s status was updated to {}\n".format(name, new_status) 
                else:
                    message = "{}'s status was updated to {}\n".format(name, new_status)
                    
                keys_df.loc[i,'status'] = new_status
                keys_df.to_csv(path + 'data/id_data.csv', index=False)
                flag = 1
                
            # Tap the button "Search next"
            driver.find_element(By.CLASS_NAME, 'lnk_otroTramite').click()
            driver.implicitly_wait(impl_wait)
            time.sleep(random.random() + 3)
            
    except Exception as e:
        print(e)
        message = 'Update error'
        
    finally:    
        driver.quit()
        
    return keys_df, flag, message



def test_check_tramites(path): #test versios
    
    flag = 0
    message = 'No updates'
    keys_df = pd.read_csv(path + 'data/id_data.csv')
    
    time.sleep(2)
        
        
    for i, row in keys_df.iterrows():
        name, key, status = row
        new_status = random.choice(['Verification', 'Deleted'])
        
        if new_status != status:
            print('Status was updated')
            if flag:
                message += "{}'s status was updated to {}\n".format(name, new_status)
            else:
                message = "{}'s status was updated to {}\n".format(name, new_status)
            keys_df.loc[i,'status'] = new_status
            keys_df.to_csv(path + 'data/id_data.csv', index=False)
            flag = 1
    return keys_df, flag, message



def check_id(key):
    flag = True

    if re.fullmatch('(\d){9,11}', key) == None:
        flag = False
        return flag
    
    try:
        
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(options=options)
    
        driver.get('https://mitramite.renaper.gob.ar/')
        driver.implicitly_wait(30)
        driver.find_element(By.ID, 'tramite').send_keys(key)
        driver.find_element(By.ID, 'btn-consultar').click()
        driver.implicitly_wait(30)
        warnings = driver.find_elements(By.ID, 'lbl_warning')
        
        driver.quit()
        
        if len(warnings) != 0:
            flag = False
            
    except Exception as e:
        flag = False
        print(e)
    finally:
        return flag
        
def test_check_id(key):
    flag = True

    if re.fullmatch('(\d){9,11}', key) == None:
        flag = False
    return flag
    
def update_df(path, name, key):
   df = pd.read_csv(path + 'data/id_data.csv')
   df = df.append({'name': name, 'key': key, 'status': 'Added'},
                  ignore_index=True)
   df.to_csv(path + 'data/id_data.csv', index=False)


def main():
    print(check_tramites())


if __name__ == "__main__":
    main()
