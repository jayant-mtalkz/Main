import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import io
import ast
import requests
from datetime import datetime
from flask import Flask, jsonify
from flask import Flask, render_template
from flask import*
# import nltk
import re
# import string
# from nltk.corpus import stopwords
# nltk.download('punkt')
# nltk.download('stopwords')
# from nltk.tokenize import word_tokenize
#--------------------data pre-processing------------------------#
#dataset1
app = Flask(__name__)

def dataset():
    
    #-------------------- data preprocessing----------------------#
        
    df1 =pd.read_csv("https://mtalkzplatformstorage.blob.core.windows.net/mtalkz-files-transfer/ynX1KNPiiyFRLwS.csv")
    # df1.dtypes
    #dataset2
    df2 = pd.read_csv("https://mtalkzplatformstorage.blob.core.windows.net/mtalkz-files-transfer/Qxozys6Bpi66Cvt.csv")
    df2.dtypes
    df2.rename(columns = {'Campaign Name':'Campaign name'}, inplace = True)
    merge_dff = pd.merge(df1, df2, on ='Number',how='outer')
    merge_dff.head()
    #null value present in each column.-----
    merge_dff.isnull().sum()
    
    #-----------------Rename column-------------------
    merge_dff.rename(columns = {'Location_y':'Click Location','Location_x':'Provider Location','Campaign name_x':'Campaign name','Count':'Clicks'}, inplace = True)
    merge_dff.head()
    #remove extra column---------------
    
   

    # ---------------------dealing with null values-------------------
    merge_dff= merge_dff.fillna(value={'Provider Location':'unknown' , 'Provider':'unknown' , 'Browser':'unknown' , 'Platform':'unknown'   ,'Status':'No','Clicks':0,'Click Location':'unknown'})
    merge_dff.drop(['Campaign name_y'], inplace = True,axis = 1)
    merge_dff['Clicks'] = merge_dff['Clicks'].astype(int)
    merge_dff['Status'] = merge_dff['Status'].replace(['Delivery','Other'], ['Delivered','Failed'])


    d = dict();

    #-----------------------calculate diffrence btwn sent-time and delivered time---------#
    # convert send time and Delivered time into datetime datatype----
    merge_dff["Send Time"] =  pd.to_datetime(merge_dff["Send Time"], infer_datetime_format=True)
    merge_dff["Delivered Time"] =  pd.to_datetime(merge_dff["Delivered Time"], infer_datetime_format=True)
    #Diffrence of send time and delivered time.-------
    merge_dff["Diffrence Time"] = merge_dff["Delivered Time"] - merge_dff["Send Time"]
    seconds = merge_dff["Diffrence Time"].astype('timedelta64[s]').astype(np.int32)
    merge_dff["Diffrence Secs"] = seconds
    # print(merge_dff.dtypes)

        
    #return delivered rate of caimpaign     

    total_sent = merge_dff['Message'].count()
    # print("total messages sent",total_sent)
    num_delivered = (merge_dff['Status'] == 'Delivered').sum()
    # print(f"number of messages delivered in APP1\t{num_delivered}")
    delivered_rate = (num_delivered / total_sent) * 100
    d['delivered_rate'] = delivered_rate


    # undelivered rate-----------


    total_sent = merge_dff['Status'].count()
    num_undelivered = (merge_dff['Status'] == 'Failed').sum()
    # print("number of undelivered msges\t",num_undelivered)
    undelivered_rate = (num_undelivered / total_sent) * 100
    d['undelivered_rate']=undelivered_rate

    #response rate-----------
        

    total_sent = merge_dff['Status'].count()
    # print("total messages sent \n",total_sent)
    clicked_msg = (merge_dff['Clicks'] > 0).sum()
    # print("number of messages clicked\t",clicked_msg)
    response_rate = (clicked_msg  / total_sent)*100
    d['response_rate']=response_rate
    

    #now calculating the non-reaction rate ---
    total_sent = merge_dff['Status'].count()
    # print("total messages sent\n\t",total_sent)
    unclicked_msg = (merge_dff['Clicks'] == 0).sum()
    # print("number of unclicked messages\t",unclicked_msg)
    notresponse_rate = (unclicked_msg  / total_sent)*100
    d['notresponse_rate']=notresponse_rate



    #  frequeancy of status of the messages
    df4 =  merge_dff.groupby('Status').size().sort_values(ascending=False).reset_index()
    df4.rename(columns =  {0:'No_of_msges'},inplace = True)
    j = df4.set_index('Status')['No_of_msges'].to_json()
    sta = ast.literal_eval(j)
    df6 = merge_dff.groupby('Status').size().sort_values(ascending=False).reset_index()
    df6.rename(columns =  {0:'No_of_msges'},inplace = True)
    
    
   #----Provider and its frequency-----------
    df5 =  merge_dff.groupby('Provider').size().sort_values(ascending=False).reset_index()
    
    df5.rename(columns =  {0:'Frequency'},inplace = True)
    i = df5.set_index('Provider')['Frequency'].to_json()
    pro = ast.literal_eval(i)
    df7 =  merge_dff.groupby('Provider').size().sort_values(ascending=False).reset_index()
    df7.rename(columns =  {0:'Frequency'},inplace = True)
    
    #fetching the ip address column from the dataset anf find user's information------
    
    
    not_null_ip = merge_dff.dropna(axis=0, subset=['IP Address'])
    IP_list = not_null_ip["IP Address"].tolist()
    
    ip = []
    city = []
    region = []
    country = []
    def get_location(ip_address):
        
        response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
        
        location_data = {
            "ip": ip_address,
            "city": response.get("city"),
            "region": response.get("region"),
            "country": response.get("country")
        }
        return location_data
        
    
    for i in range(0,5):
        response = get_location(IP_list[i])
        print(response)
        ip.append(IP_list[i])
        city.append(response.get("city"))
        region.append(response.get("region"))
        country.append(response.get("country"))
        
        
    df8 = pd.DataFrame(list(zip(ip, city, region, country)),columns =["ip", "city", "region","country"])
    print("####################################333")
    print(df8)
   
    
   
    
    
    
    
    return d,pro,sta,df6,df7
    
d,pro,sta,df6,df7 = dataset()

list = []
list.append(d)
list.append(pro)
list.append(sta)



@app.route('/', methods=['GET'])
def home():
    return 'welcome to analytics part'

@app.route('/all', methods = ['GET'])
def all():
    return jsonify(list)
  
@app.route('/diff_rates', methods=['GET'])
def insights():
    return jsonify({"diffrent rates in APP1":d})

@app.route('/provider_freq',methods =['GET'])
def provider_freq():
    return jsonify({"provider in camp1 and their freq":pro})


print("###################################33")
print(df6)
print(df7)
print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$44")
@app.route('/status',methods =['GET'])
def status():
    return jsonify({"status of messages in APP1":sta})

#pie chart showing the message status

@app.route('/matplot',methods=['GET','POST'])
def mpl():
    return render_template('matplot.html',PageTitle = 'Matplotlib')

@app.route('/plot.png',methods =['GET'])
def status_fig():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    
    # fig = df6.groupby(['Status']).sum().plot(kind='pie', y='No_of_msges', autopct='%1.0f%%')
    STATUS = ['Delivered', ' No', 'Failed']
    data = [6667,1667,1666]
    # Creating plot
    fig = plt.figure(figsize =(10, 5))
    plt.pie(data, labels = STATUS)
    return fig

# #bar chart showing the provider and its frequency

# @app.route('/matplot2',methods=['GET','POST'])
# def mpl2():
#     return render_template('matplot2.html',PageTitle = 'Matplotlib')

# @app.route('/plot2.png',methods =['GET'])
# def provider_freq():
#     fig2 = create_figure2()
#     output = io.BytesIO()
#     FigureCanvas(fig2).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')

# def create_figure2():
    
#     fig2 = df7.plot(x = "Provider", y = "Frequency", kind = "bar")
#     # plt.show()
    
  
#     return fig2




if __name__ == '__main__':
    app.run(debug = True)
  










