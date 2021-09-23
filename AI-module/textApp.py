"""
    In this file, we are creating the server side API (using Flask framework) around our AI model, so that we can integrate it within our web application,
    An API is created that will get the image path, feed it into our AI model, and get back the response of the model
"""

#Import the required libraries
from extractText import getGoogleVisionForExtraction #importing our AI model function as a module
from flask import (Flask, request, jsonify, render_template) #importing required flask libraries

#Create API endpoint to make requests
@app.route('/extract_text', methods = ['POST']) #the end url will be '/extract_text', request method would be 'POST'
def extract_text():
    if request.method == 'POST':
        file = request.files['file'] #get file from the request
    try:
        filename = file.filename #get attached file name
        file.save(filename) #save the file into the server side
        file_ext_type = os.path.splitext(filename)[1][1:] #find the file extension type from the filename
        #calling the AI module to extract the text from given image
        res_list, accuracy = getGoogleVisionForExtraction(filename, file_ext_type) #passing filename along with extension type
        #check if the response of the AI module is None
        if(res_list != None): #if not None then it means we got the text in response
            res_dict = {} #declaring a dictionary to save the response in key-value pairs
            res_dict['accuracy'] = accuracy +'%' #save the average accuracy against 'accuracy' key
            res_dict['extracted_text'] = res_list #save the text_list aginast 'extracted_text' key
            return jsonify(res_dict) #return the dictionary in JSON form as a response of the API
        else:
            #if response of the AI module is NONE, it means an error is occured
            #return the error message to let the user know
            error = {'message': 'Error occured while extracting the data'}
            return jsonify(error)
    except:
        #if anything breaks in the API process then return the error message
        error = {'message': 'Something went wrong'}
        return jsonify(error)


'''
    This part of the code will run only if we run this code-file directly (let say for testing purposes), 
    if we import the functions of this file into the other files then this part will not get imported.
'''
if __name__ == '__main__':
    #Server configutation
    #Run the server on localhost at port number 5000 and make it multi threaded  to handle the multiple requests at a time
    app.run(host='0.0.0.0', port=5000, threaded=True)
