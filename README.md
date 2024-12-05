# potato-disease
This is a potato disease classification project.
i am trying to create the potato disease classification project using CNN algorithm. our task is to implement the CNN without using any tensorflow or pytorch libraries. but, i am trying to train my model by using mixed types that is: some part of CNN by using libraries and some part without using libraries. Here, I have implemented the class CustomConv2D and MixedCNN without using libraries i.e by defining them as custom object. However, the data get trained with better accuracy.
But the problem arise while loading into the flask file. It throws error : "ould not locate class 'MixedCNN'. Make sure custom classes are decorated with 
`@keras.saving.register_keras_serializable()`.
however, i havenot uploaded the trained file due to the size problem. I uploaded the mixedmodel file where the entire backend code to train ml is constructed and app.py of flask, just to solve this only problem of importing the saved model.
For dataset I have taken : https://www.kaggle.com/datasets/emmarex/plantdisease   {from here, 3 folders: Potato__earlyblight, potato__lateblight and potato__healthy are taken} and saved under folder " PlantVillage"
