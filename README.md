# GuanYu
This project is use machine learning algorithm Random Forest to find hidden camera from Meraki platfom network flow data

You can run wechat/train.py to get a model and save to wechat/save/, the command line is:

export PYTHONPATH=$PYTHONPATH:/home/ubuntu/django

cd ~/django

python -m devnav.wechat.train

              precision    recall  f1-score   support

           0       0.99      1.00      1.00       301
           1       1.00      0.92      0.96        25

    accuracy                           0.99       326
    
   macro avg       1.00      0.96      0.98       326
   
weighted avg       0.99      0.99      0.99       326



We build a webserver based django to set up a communication between server and wechat public account, we set up a timed job 
in wechat/views.py which extract network flow data of previous day, feed them to trained model, find hidden cameras and store 
to database.

You can input 'camera?' in wechat to get respond from webserver which check if there are hidden cameras by reading database
