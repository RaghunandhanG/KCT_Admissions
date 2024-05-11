import os
import easyocr
import fitz
from together import Together
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()



def get_prompt(text, type):
    if type.lower() == 'marksheet':
        marksheet_prompt = f'''The following is the extracted unstructured text data from a 10th standard marksheet of an Indian student. The different extracted words are separated in order by commas.

Your task is only to create a JSON containing key-value pairs for the given key format in order.

The below mentioned parameters should be the keys of the JSON in the following given format. If you are not confident at any of the value for the following key, make it as to None.

The unstructured data : {text}
The json key format : [Certificate Number, Board of Examination, Name, Month & Year, Father Name, Mother Name, Subject (dictionary with Multiple key), Total Marks, DOB, Roll Number, Medium of Instruction, Permanent Register Number, TMR Code, School Name, Place, District, State]
    
    NOTE : The order of the key format must be maintained as given above.
    
IMPORTANT : Subject key must contain a dictionary as value with different subject name and respective mark as value.
IMPORTANT : Return only a json string with only given keys and avoid any other information in the output.'''
        return marksheet_prompt

    elif type.lower() == 'aadhaar':
        aadhaar_prompt = f'''The following is the unstructured text data of a indian aadhar card of a student extracted using the EasyOCR package. The different extracted words are separated in order by commas.

Your task is only to create a JSON containing key-value pairs for the given key format in order.

The below mentioned parameters should be the keys of the JSON in the following given format. If you are not confident at any of the value for the following key, make it as to None.

The unstructured data : {text}
The json key format : [Enrollment Number, Name, Father Name, Place, District, State, Phone number, Aadhaar number, DOB, Gender]

    NOTE : The order of the key format must be maintained as given above.

IMPORTANT : Return only a json string for given keys and avoid any other information in the output.
'''
        return aadhaar_prompt

    else:
        general_prompt = f'''The following is the unstructured text data of a student extracted using the EasyOCR package. The different extracted words are separated in order by commas.

Your task is only to create a JSON containing key-value pairs for the given key format in order.

The below mentioned parameters should be the keys of the JSON in the following given format. If you are not confident at any of the value for the following key, make it as to None.

The unstructured data : {text}
The json key format : [Enrollment Number, Name, Father Name, Place, District, State, Phone number, Aadhaar number, DOB, Gender]

    NOTE : The order of the key format must be maintained as given above.

IMPORTANT : Return only a json string for given keys and avoid any other information in the output.
'''
        return general_prompt

def get_json(text,type):
    
        client = Together(api_key=os.getenv('TOGETHER_API_KEY'))

        prompt = get_prompt(text,type)

        response = client.chat.completions.create(
            model="meta-llama/Llama-3-70b-chat-hf",
            messages=[{"role": "user", "content": prompt}],)
        


        msg = response.choices[0].message.content
        print(msg)
        return msg


def convert_pdf_to_images(pdf_path, output_folder, docname, zoom=2):

  doc = fitz.open(pdf_path)
  imgs = []
  print("Started Converting to images")
  os.makedirs(output_folder, exist_ok=True)

  BASE_DIR = os.path.dirname(__file__) + '\imgs'
  print(BASE_DIR)
  for i, page in enumerate(doc):
      pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
      filename = os.path.join(BASE_DIR, f"{docname}page_{i+1}.png")
      print(filename)
      pix.save(filename)
      imgs.append(filename)
  print(f"Converted PDF to {len(doc)} images in {output_folder}")
  return imgs



def convert_to_text(imgs):

    
    reader = easyocr.Reader(['en'] , gpu = True)  

    text = []
    for image_path in imgs:
        print('Converting to text')
        text.extend(reader.readtext(image_path))
        print('Converted')

    return text

def get_unstructured_data(imgs):
    text = convert_to_text(imgs)
    for i in range(len(text)) :
        text[i] = text[i][1:]
        
    easyocr_detection = ''
    for i in text:
        if i[1] > 0.5:
            easyocr_detection += (i[0]) + ', '
    return easyocr_detection



def get_file_names_with_folder(folder_path):

    file_names = []
    
    for file_name in os.listdir(folder_path):

        if os.path.isfile(os.path.join(folder_path, file_name)):

            file_names.append(os.path.join(folder_path, file_name))
    
    return file_names

def extract_last_index(raw_text):
    for i in range(-1 , ~len(raw_text) , -1):
      if raw_text[i] == "}":
        return i

def extract_first_index(raw_text):
    for i in range(len(raw_text)):
      if raw_text[i] == "{":
        return i

def retrieve_json_from_text(text):

    print("In retrieve function " , text)
    
    json_data = eval(text)

    print(json_data)
    print(type(json_data))

    return json_data

def start_processing(file_names,keys):
    # keys = ['marksheet','aadhaar']
    file_path = []
    BASE_DIR = os.path.dirname(__file__)
    for pdf in file_names:
        print("Starting 1st pdf", pdf)
        filename = secure_filename(pdf.filename)
        path = os.path.join(BASE_DIR, 'uploads', filename)
        pdf.save(path)
        file_path.append(path)
        # with open(file_path, 'wb+') as destination:
        #         for chunk in pdf.chunks():
                    # destination.write(chunk)
    
    print("Completed paths")
    

    json_array = []
    
    for pdf_path, key in zip(file_path, keys):
        type(pdf_path)

        imgs = convert_pdf_to_images(pdf_path,"imgs" , pdf_path[0:-4], zoom=2)
        text = get_unstructured_data(imgs)
        print(text)
        raw_text = get_json(text, key)
        
        print("In funcion processing " , type(raw_text))
        
        
        json_array.append( retrieve_json_from_text(raw_text[extract_first_index(raw_text) : extract_last_index(raw_text)] + '}') )
        
    return json_array
    