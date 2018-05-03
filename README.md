# TalkingData  Fraud Detection


## 1. Barckground and Introduction

### 1.1 TalkingData Company
---


> Founded in 2011, TalkingData is China’s largest independent **Big Data service platform**. ... include **industry-leading solutions** such as mobile app & gaming analytics, mobile ad tracking, enterprise Smart Marketing Cloud, and consulting. 

Genearlly speaking, [TalkingData](https://www.talkingdata.com/product-AdTracking.jsp?languagetype=en_us) is a third-party platform, which provides analytics for small and medium size moblie applications.

### 1.2 TalkingData's AdTracking Service
---

TalkingData's AdTracking Service provides business insights using mobile's clicking amoungt in a short period (mainly for **advertisements**). Like an outsourcing service, TalkingData will charge you in different modes. 

![Adtracking](images/adtrac.png)

### 1.3 TalkingData's Anti-Cheating Service
---
If we are using the AdTracking Service, we will have this dashboard to monitor our applications operations situations. For Anti-Cheating part, TalkingData will rank the "Fraud Click" based on several calculations. Even if we want to explore more about this service, we still stop here because we need to register an account.
 
![dashboard](images/dashboard.png)

## 2.0 Business Value and Objective

This section will explain the business value of this project and data competition. Based on these business values, our objective and task are valueable not only for TalkingData but also data mining.

#### 2.1 Pay-per-click (PPC) Business Model
---

For some mobile applications (ios or Android), they are using Pay-per-click (PPC) model, which will help direct traffic to their applications. Genearlly speaking, they want to increase the number of downloads using internet advertising companys. If users click this advertisment, the advertising company will charge based on each click. Overall, higher click volume will lead to high download rate. This part is related to **Click-through rate (CTR)**.

**Motivation to cheat:** High Click Times will increase these company's income but the application download times will not increase.

#### 2.2 Malicious Parties
---

Besides the advertising companys, competitors and other **malicious parties** will use clicks to affect the daliy operation of mobile applications. These actions will increase the workload of current server.

**Motivation to cheat:** "Attack" the sever with malicious purposes.

#### 2.3 Objective

With all these informaiton, our task is to detect the "click fraud" behavior. To achieve this goal, in this document, we want to estiamte :

- **Probability of Application Download** : Predicted probabiliy of each click to download the application 


## 3. Data Exploration 

Becasue the total training data size is really **huge** (184 millions lines), we only use part of the data (100k lines) for exploration analysis.

### 3.1 Data Basic Information

- Time Period : From **2017-11-06** to **2017-11-09** (4 days)
- Original Fields : 7 variables and 1 target variables

All fields are as follow :

| Variable Name  | Explaination | Example |
| ------------- | ------------- |------------- |
| ip  | ip address of click  | 87540|
| app  | app id for marketing  |12|
|device| device type id of user mobile phone (e.g., iphone 6 plus, iphone 7, huawei mate 7, etc.)|1|
|os| os version id of user mobile phone|13|
|channel| channel id of mobile ad publisher|497|
|click_time| timestamp of click (UTC)|	2017-11-07 09:30:38|
|attributed_time| if user download the app for after clicking an ad, this is the time of the app download| NaN|
|is_attributed| the target that is to be predicted, indicating the app was downloaded|0|
