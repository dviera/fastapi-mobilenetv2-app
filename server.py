from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import base64
from io import BytesIO
from PIL import Image
import numpy as np
import pandas as pd
import urllib
import matplotlib.pyplot as plt

from plotnine import aes, ggplot, geom_segment, geom_point, coord_flip, theme_minimal, labs, theme, element_text, guides

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.applications.mobilenet_v2 import decode_predictions
from tensorflow.keras.preprocessing import image
import tensorflow as tf


#-------------- KERAS MODEL --------------#

# def load_model ():
#     # global mobile
#     mobile = MobileNetV2()
#     mobile.save("model")

# load_model()

mobile = tf.keras.models.load_model("model")


#------------------ PLOT -----------------#

def lollipop(data):
    data = data.sort_values(by=['probability']).reset_index(drop=True)
    custom_order = pd.Categorical(data['label'], categories = data.label)
    data = data.assign(label_custom = custom_order)

  
    p = ggplot(data, aes('label_custom', 'probability')) + \
        geom_point(color = "#88aa88", size = 4) + \
            geom_segment(aes(x = 'label_custom', y = 0, xend = 'label_custom', yend = 'probability'), color = "#88aa88") + \
                coord_flip(expand=True) + \
                    theme_minimal() + \
                        labs(x="", y="probability", title = "Most Likely Object") + \
                            guides(title_position = "left") + \
                                theme(plot_title = element_text(size = 20, face = "bold", ha= "right"))

    fig = p.draw()
    figfile = BytesIO()
    plt.savefig(figfile, format='png', bbox_inches='tight')
    figfile.seek(0)  # rewind to beginning of file
    figdata_png = base64.b64encode(figfile.getvalue()).decode()
    return p, figdata_png

#------------------ FASTAPI -----------------#

app = FastAPI()


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



@app.api_route("/")
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.api_route("/about.html")
async def about(request: Request):
    return templates.TemplateResponse('about.html', {'request': request})

@app.post("/")
async def predict(request: Request):
    
    # GET REQUESTER IP :P
    #print(request.client.host)
    
    if request.method == "POST":
        data = await request.form()
        
        # UNDERSTANDING THE DATA-------
        #print(data) #FormData [('image', <starlette.datastructures...)]
        #print(data['image']) #UploadFile

        # READ IMAGE
        test = await data['image'].read() #read file

    
        # UNDERSTANDING THE DATA-------
        #print(data['image'].content_type) # image/png
        #print(data['image'].file) # SpooledTemporaryFile

        # CHECK IF THE REQUESTER LOADED A CORRECT FORMAT OR NOT
        if data['image'].content_type not in ['image/png', 'image/jpeg', 'image/jpg']:
            display = True
            warn = "This is not a picture. Please choose a png, jpeg or jpg format!"

            #return templates.TemplateResponse('index.html', {'request': request, 'warning': warn, 'display': display})
            return {'status': 'no-supported-plot', 'result': warn}

        else:
            display = False
            warn = ""
            
            try:
                img = Image.open(BytesIO(test))
                dimensions = np.array(img).shape
            
                if len(dimensions) > 2 and dimensions[2] == 4:
                    img = img.convert('RGB')
                    #print(np.array(img).shape)

                img = img.resize((224, 224))
                img = image.img_to_array(img)
                img = np.expand_dims(img, axis=0)
                img = preprocess_input(img)
                preds = mobile.predict(img)
                preds = decode_predictions(preds)

                data = {}
                data["success"] = True
                data["predictions"] = []

                for (imagenetID, label, prob) in preds[0]:
                    r = {"label": label, "probability": float(prob)}
                    data["predictions"].append(r)
                
                
                predictions = pd.DataFrame(data['predictions'])
                p, plot = lollipop(predictions)

                
                #return templates.TemplateResponse('index.html', {'request': request, 'warning': warn, 'display': display, 'plot': plot})
                return {'status': 'ok-plot', 'result': plot}

            except:
                display = True
                warn = "Problem with your picture. Probably broken!"
                #return templates.TemplateResponse('index.html', {'request': request, 'warning': warn, 'display': display})
                return {'status': 'error-plot', 'result': warn}
                


            
