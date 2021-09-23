"""
    This is the backend code file in flask for the web application where we are creating the endpoints to handle the flow of the web-pages,
    The whole web work flow (like what to show after which button, what page to show) along with integration of our AI API, will be handled in this file
"""

#import required libraries
from flask import Flask, render_template, request, redirect, send_from_directory, send_file #required flask libraries
from werkzeug.utils import secure_filename #required to filter out spam files
import requests #required to make API requests
import pathlib #required to get system level path
import os #required to run system level commands
from urllib.request import urlretrieve as retrieve
#declare flask app name
app = Flask(__name__, template_folder='templates') #mention template folder to let it know where out HTML files are stored

PARENT_PATH = str(pathlib.Path(__file__).parent.resolve()) #get current folder directory
UPLOAD_FOLDER = PARENT_PATH + '/static/upload' #append the path to save the uploaded images
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'} #mention allowed extensions while attaching the image to the webpage
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER #attach upload folder path with the server configuration 


#function to make API requests
def makeRequest(card_img_path):
    """
    This function takes the image path, gets the image/file bytes, make request to our AI API to process the image and gets the results.
    
    Parameters: img_path : path of the given image
    Returns: [JOSN] :[Response of the AI API]
    """
    try:
        files = {'file': open(card_img_path, 'rb')} #get bytes from the given image/file path
        url = 'http://3.97.132.230:5000/extract_text' #endpoint of our AI API
        response = requests.post(url=url, files=files) #get the response of the API
        return response #return the response
    except:
        #return NONE if anything breaks while making API requests
        return None
    
    
'''
Create backend endpoints to switch between web-pages flow
'''
#This inner function would be called when user will simple hit our URL (for exmaple: 'www.webiste/')
#It will open up the home page
@app.route('/')
def index():
    return render_template('index.html') #render template opens up our give HTML file, in this case it will render/open the index.html file which is our home page file


#This inner function would be called when user will attach the image and click on the 'SUBMIT' button
#It will get the image from the web page, pass it to the API-request function to process it, get back the results and open up to the next web-page
@app.route('/extract_text', methods=['POST', 'GET'])
def validateimage():
    try:
        file = request.files['customFile'] #get the attached image/files
        filename = secure_filename(file.filename) #filet out spam file and get filename
        file.save(os.path.join(UPLOAD_FOLDER, filename)) #save the file to the current working directory
        logo = file.filename #save the filename to a separate variable to pass it to the next page
        logo = logo.replace(" ", "_") # replace the spaces with underscore in the filename
        image = UPLOAD_FOLDER + '/' + logo #integrate the filename with the upload folder path to get the full image path
        
        response = makeRequest(image) #call the makeRequest function by pasisng the image path, to make request to the AI API
        response = response.json() #get the API response of the function in json form 

        logo = "static/upload/" + logo #replace the image path with the current one
        return render_template('second.html', data=response, logo=logo) #return the response along with image path and opens up the next web page
    except:
        #if anything breaks in the API request API then stay on the home page
        return render_template('index.html')

    
#This inner function would be called when user will click on the 'DOWNLOAD' button
#It will get the image extension along with the local image path from the web page and download it in the browser
@app.route('/download', methods=['POST', 'GET'])
def download():
    message = request.form.get('message') #get text from the text area of the web page
    radiobutton = request.form.get('radiobut') #get extension type of the downloadable file
    data = message #save the given text into the local variable
    data = data.replace(',', ' ') #replace the additional commas with whitespace in the text
    
    filename = 'extracted-text.' + str(radiobutton) #create a filename along with extension
    #opens-up the file with above filename, write the text into it
    with open(filename, 'w') as f:
        f.write(data)
    
    #call the next function endpoint to download these files
    return redirect(f'/get-files/{filename}')


#This inner function would be called when user will click on the 'DOWNLOAD' button
#It will get the image extension along with the local image path from the web page and download it in the browser
@app.route('/get-files/<path:path>', methods=['GET', 'POST'])
def get_files(path):
    try:
        #call the send_file function to download the files into the browser
        return send_file(path, as_attachment=True) #passing image/file path and setting as_attachment to True to make it downloadable
    except FileNotFoundError:
        #if anything breaks then return NONE
        return None

    
'''
    This part of the code will run only if we run this code-file directly (let say for testing purposes), 
    if we import the functions of this file into the other files then this part will not get imported.
'''
if __name__ == '__main__':
   port = int(os.environ.get('PORT', 5000))
   app.run(host='0.0.0.0', port=port, debug=False)
 #run the server on the localhost with default port of 5000

