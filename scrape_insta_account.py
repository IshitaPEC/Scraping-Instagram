from selenium import webdriver
from time import sleep
import os
from bs4 import BeautifulSoup
import requests
import shutil
from xlsxwriter import Workbook

class App:
    def __init__(self,username='ishitaaroramohali@yahoo.in',password='nonmedlifesucks',target_username='ishita_arora_2000', path=r"C:\\Users\\Dell\\Desktop\\instaphotos"):
        self.username = username
        self.password = password
        self.path=path
        self.all_images=[]
        self.error = False
        self.target_username = target_username
        self.main_url = 'https://www.instagram.com/accounts/emailsignup/'
        self.driver= webdriver.Chrome(r"C:\Users\Dell\Downloads\chromedriver_win32\chromedriver.exe")
        self.driver.get(self.main_url)
        sleep(3)
        self.log_in()
        if self.error is False:
            self.close_dialogue_box()
            self.open_target_profile()
        if self.error is False:
            self.scroll_down()
        if self.error is False:
        #We have created a folder where we will keep all the photos that we need
            if not os.path.exists(self.path):
                os.mkdir(self.path)
            self.download_images()
        sleep(3)
        self.driver.close()


#Whenever we open someones profile, in the first attempt, we will only find 12 photos loaded -> 4 rows of 3 photos each
#However whenever we scroll down we have 12 more photos downloading
#So we need to find the number of scrolling down that is needed
    def scroll_down(self):
        try:
            #At the top of the profile, we have the number of the posts mentioned
            #Alternate method to find_by_partial_link_text
            no_of_posts = self.driver.find_element_by_xpath('//span[text()=" posts"]').text
            #Find the numerical part from the string text
            no_of_posts = no_of_posts.replace(' posts', '')
            no_of_posts = str(no_of_posts).replace(',', '')  # 15,483 --> 15483
            self.no_of_posts=int(no_of_posts)
            #From the no. of posts and we know the number of posts in 1 scroll-> we calculate the number of scrolls needed
            no_of_scrolls=1
            if self.no_of_posts > 12:
                no_of_scrolls = int(self.no_of_posts / 12) + 5
            try:
                for value in range(0,no_of_scrolls):
                    #Whenever you have to interact with javascript, we use driver.execute_script method
                    self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                    sleep(2)
            except Exception as e:
                self.error=True
                print(e)
                print('Some error occured while trying to scroll down')
            sleep(10)
        except Exception:
            print('Could not find no of posts while trying to scroll down')
            self.error = True


    def write_descriptions_to_excel(self,description_path,all_images):
        #Create path inside excel folder
        # Create a workbook
        #We already have a description folder inside our main instaphotos folder
        #The pupose of this is to create an excel chart in the description folder
        #Why we use os.path.join() so that things like adding '/' etc are taken care of
        workbook = Workbook(os.path.join(description_path,'description_chart.xlsx'))
        # Add a worksheet
        row=0
        worksheet = workbook.add_worksheet()
        #These are titles of the 2 columns:-> 'Image Name' and 'Caption'
        worksheet.write(row, 0, 'Image Name')
        worksheet.write(row, 1, 'Caption')
        row+=1
        # Write Worksheet - parameters-(row,column,value)
        #Purpose of enumerate is to give us an index in addition to image
        for index,image in enumerate(all_images):
            #Note that img tag has an alt field which contains the caption
            #However there might not be any caption and for that purpose we use try and except block
            try:
                caption=image['alt']
            except Exception:
                caption='No Caption Exists'
            worksheet.write(row, 0, 'image_'+str(index)+'.jpg')
            worksheet.write(row, 1, caption)
            row+=1
        # Close Workbook
        workbook.close()

    def download_description(self,all_images):
        #Create a folder for description inside the insta photos folder
        description_path=os.path.join(self.path,'description')
        #If this path does not exist then create folder else continue
        if not os.path.exists(description_path):
            os.mkdir(description_path)
        self.write_descriptions_to_excel(description_path,all_images)
        #The above function call would yield to writing the descriptions in an excel file
        #Below, we create an independent text file for each description:
        for index,image in enumerate(all_images):
            try:
                description= image['alt']
            except:
                description="No Description exists"
            #Create a text file with the following file name
            file_name= 'descriptions'+ str(index) + '.txt'
            #Now create the path for this file
            file_path= os.path.join(description_path,file_name)
            #This is the source link 'src' for the image corresponding to which we are storing the caption
            link= image['src']
            #Now we write the caption and link to our file, inorder to facilitate the writing of emogis, we have to encode it into binary
            with open(file_path,'wb') as file:
                file.write(str('link'+ str(link) + '\n' + 'Description:' + description).encode())


    def download_images(self):
        # Use Beautiful Soup if possible, avoid selenium wherever possible
        # Wherever there is an <img> tag , we are using that tag to find our image
        # We want to find the 'src' attribute for every img that exists
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        self.all_images= soup.find_all('img')
        print('Length of all images', len(self.all_images))
        self.download_description(self.all_images)
        for index, image in enumerate(self.all_images):
            filename = 'image_' + str(index) + '.jpg'
            #Here self.path gives the name of our directory and the filename refers to individual name of the images!
            image_path = os.path.join(self.path, filename)
            link = image['src']
            try:
                print('Downloading image', index)
                #The method below is a way to download our image given the sourcelink into the desired folder on our system
                response = requests.get(link, stream=True)
                #We basically write/copy the image we get from the link into our filename which we have established for the link
                with open(image_path, 'wb') as file:
                    shutil.copyfileobj(response.raw, file)  # source -  destination
            #Incase the url is a url which does not open up, is unable to be downloades, is not in the format that we want
            #Then we give an exception
            except Exception as e:
                print(e)
                print('Could not download image number ', index)
                print('Image link -->', link)



    def open_target_profile(self):
        try:
            search_bar = self.driver.find_element_by_xpath('//input[@placeholder="Search"]')
            search_bar.send_keys(self.target_username)
            #Whenever we enter in the search bar:-> suggestions pop up, hence as a full proof method we rather change the url to the target profiles user
            target_profile_url = 'https://www.instagram.com/' +  self.target_username + '/'
            self.driver.get(target_profile_url)
            sleep(3)

        except Exception:
            self.error = True
            print('Could not find search bar')


    def close_dialogue_box(self):
        # reload page
        #In case any dialogue box opens up;  we close it
        sleep(2)
        #Refresh page by searching or accessing the same page
        self.driver.get(self.driver.current_url)
        sleep(3)

        try:
            sleep(3)
            #Better method of using partial link text method
            not_now_btn = self.driver.find_element_by_xpath('//*[text()="Not Now"]')
            sleep(3)
            not_now_btn.click()
            sleep(1)
        except Exception:
            pass

    #Sometimes the settings window might open up and we would want to close it:
    #We have window_handles which keeps a track of reference of the windows that we have.
    #self.driver.switch_to() is used to switch to another window
    def close_settings_tab(self):
        try:
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception:
            pass


    def log_in(self, ):
        #First the sign-up page opens up
        #We find the login button and click that
        try:
            #Find the login button
            tag = self.driver.find_element_by_xpath("//div[@id='react-root']//div[@class='gr27e']//a")
            tag.click()
            sleep(3)
        except Exception:
            self.error = True
            print('Unable to find login button')
        #Now we fill our login form
        else:
            try:
                #We look for our user name and password input box
                user_name_input = self.driver.find_element_by_xpath('//input[@aria-label="Phone number, username, or email"]')
                #We send the keys of Username
                user_name_input.send_keys(self.username)
                sleep(1)
                password_input = self.driver.find_element_by_xpath('//input[@aria-label="Password"]')
                #We send the keys of the password
                password_input.send_keys(self.password)
                sleep(1)
                user_name_input.submit()
                #We can submit either using user_name.submit() or password.submit() both will lead to submission of the form
                #We must close the settings tab in order to move to our home page
                self.close_settings_tab()
                sleep(1)

            except Exception:
                print('Some exception occurred while trying to find username or password field')
                self.error = True



if __name__ == '__main__':
    app=App()
