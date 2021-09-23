"""
    In this file, we are extrating the text form the given image/file using Google AI model,
    there are two functions, one for preparing the AI model and to make request, 
    second to extracting the text using given offset or pixel values.
"""

#Import the required libraries
from google.cloud import documentai_v1beta3 as documentai #required libraries from the Google Cloud SDK

def get_text(doc_element: dict, document: dict):
    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    
    Parameters: doc_element : offset values, document : the whole response of the model
    Returns: [string] :[extracted text from the offset values]
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return response


def getGoogleVisionForExtraction(img_path, ext_type):
    """
    This function gets the image, prepares the Google AI model, makes the request to the model using given image, 
    and gets the response.
    
    Parameters: img_path : path of the given image, ext_type : extension type of the image/file
    Returns: [list] :[list of extracted text values from the given file], [string]:[average accuracy value]
    """
    try:
        # Instantiates a Google AI client to prepare the model and make request to it
        client = documentai.DocumentProcessorServiceClient()
        #Here is the endpoint of the Google AI model, that we create on Google cloud platform (GCP)
        #When you create the model on GCP, it provides you the credentials and IDs, that gonna be used here
        name = 'projects/391000548895/locations/us/processors/67d48021b176d3b3'
        
        # We have to tell the AI model which kind of image is going to be feeded, 
        # so here we are setting the applicationType value according to our extenstion type 
        if(ext_type == 'pdf'):
            applicationType = 'application/pdf'
        elif(ext_type == 'png'):
            applicationType ='image/png'
        else:
            applicationType = 'image/jpeg'
        
        #AI model takes the image as bytes, 
        # so we are gonna read the image/file as bytes into the memory from the given path.
        with open(img_path, "rb") as image:
            image_content = image.read()
        
        # Now that, our image and endpoint are ready, so lets convert them into parameters
        document = {"content": image_content, "mime_type": applicationType}
        # Configure the process request
        request = {"name": name, "document": document}

        # Make a request to the AI model using our parameters
        # process_document is Google SDK function that provides the facility to make the request
        # It recognizes text entities in the given image/file
        result = client.process_document(request=request)
        
        #we got the results from the AI model, lets dive deep into the response and get the extracted text
        document = result.document
        document_pages = document.pages
        score = 0 #declaring variable to calculate the accuracy score 
        res_list = [] #declaring a list to save the response 
        
        # We get raw response form the AI model that includes various extra information that is not required
        # So to filter it out, lets iterate over the response using loops and read the text recognition output from the processor
        for page in document_pages:
            paragraphs = page.paragraphs
            for paragraph in paragraphs:
                paragraph_text = get_text(paragraph.layout, document) #calling the get_text function to extract the text form given offsets
                perScore = paragraph.layout.confidence*100 #calculating the accuracy for single fetched line
                score = score + perScore #adding it to the prevoiud score, to calculate the average later
                res_list.append(paragraph_text) #saving the extracted text into the list
            
        accuracy = round(score/len(paragraphs)) #calculating the average accuracy by dividing the total score to the number of offsets
        
        #Our intial list gets end-of-line characters within the response
        #so let get rid of them as we want to have a clean response
        new_list = [] #declaring a list to save the clean text
        #iterate over the prevoud list and remove the end-of-lines from each text value
        for item in res_list:
            new_item = item.splitlines() #removing eof characters
            for sub_item in new_item: #iterating over the response list of eof function
                new_list.append(sub_item) #saving the text into our new list
                
        return new_list, str(accuracy) #returning the response (text list and avergae accuracy)
    except:
        #return nothing if anyting breaks in the whole text extraction process
        return None, None
    
    
'''
    This part of the code will run only if we run this code-file directly (let say for testing purposes), 
    if we import the functions of this file into the other files then this part will not get imported
'''
if __name__ == '__main__':
    img_path = 'path_to_folder/bill.png' #image_path
    res, acc = getGoogleVisionForExtraction(img_path, 'png') #calling the AI model for testing
    print(res) #printing the results