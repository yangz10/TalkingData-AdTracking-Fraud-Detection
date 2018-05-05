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
<p align="center">

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
</p>

Actual Dataset :

![dataset](images/dataset.png)

#### Chanllenge :

- Data Size : Large data is very hard to train and takes time
- Few Fields : Unlike other dataset, all these fields are not so intuitive.

Although we don't need to clean some data, we will focus more time on feature engineering.

### 3.2 Current Data Situations

To save time, I borrow some figures from: [https://www.kaggle.com/yuliagm/talkingdata-eda-plus-time-patterns](https://www.kaggle.com/yuliagm/talkingdata-eda-plus-time-patterns) and [https://www.kaggle.com/yuliagm/talkingdata-eda-plus-time-patterns](https://www.kaggle.com/yuliagm/talkingdata-eda-plus-time-patterns)

**At first, we want to figure out the unique values of all different features.** 

![disc](images/disc.png)

Actually, the above figure makes sense. Genearlly speaking, users will visit the app store with different IPs to download limited applications. Although using different devices, they may be directed by certain channels.

**In terms of the actual download percentage:**

<img src="images/download.png"  width="400" />

Amoung all data, the actual conversion rate is quite low. However, this conversion rate is **too low**. Indeed, some fraud click exit. 

**Without figuring out contribution of acutal IP or devices, we want to know more about the time pattern:**

![timepattern.png](images/timepattern.png)

From the above graph, people will click this dataset mainly from 23 pm to 15 pm. It is not realistic. Who will click the app from 3am - 5am ? Also, the bellow figure does not make sense for me.

![converstion](images/converstion.png)

### 3.3 Insights and Assumptions	

To create more useful features, we need to understand the behaviors of fraud click. Through some assumptions, I try to extend features step by step.

#### Assumptions 1.0 : Fraud clicks muth link to certain channel.

If I want to cheat using programming script, I will try to mask my IP address. Based on my own web scrawler experience, I will use a IP pool to mask my IP addresses. However, I can't mask the "finger print" - operating system (os) and other information. 

For example, if I need to increase the click amount for a certain app in a certain channel, we may use our current devices although we also will apply some anti-detection approaches. As a consequence, the device, os and other information should be the same.

**Conclusion 1.0 : Freqency of Devices and OS or other fields may help**

#### Assumptions 2.0 : Time.

If a new click happens, we can check historical data based on the timeline and then judge whether this is a fraud click. As a result, we should focus on time feature. 

For example, the interval between two click may be a very important features.

**Conclusion 2.0 : We should sort data based on timeline or calculate some features based on this.**


#### Assumptions 3.0 : Some "cheaters" are not so "smart".

For some technical reasons, some cheaters may not change IP address frequently. If the IP address is blocked, they can change IP immediately.

For them, chaning IP address increases cost for them. 

**Conclusion 3.0 : When create features, we still should consider IP address.**
 
 
## 4.0 Feature Enginerrring

We borrow ideas from [https://www.kaggle.com/nanomathias/feature-engineering-importance-testing](https://www.kaggle.com/nanomathias/feature-engineering-importance-testing) 


#### 1.Next Click 

After sorting all data based on time, we will caculate the time interval to for next click using similar app, os or other informaiton. We use create all realted features. 

#### 2.Previous Click 

Similar to **Next Click**, we also check back about the data.

#### 3.Cumulate Sum

According to previous assumptions, we also calculate previous clicks using same devices.

#### 4.Statistics

Mean and variance are calculated because they measure the stationary of certian data series. If the series fluctuates frequentely, these metrics will have large changes.

#### 5. Deep Learning

After creating the final metrics, we use neutral networks (multi-layer perceptions) to help us do feature engineering. A very deep neutral network helps us tranfrom each category features at first. Then, we compress all these data into 10 dimensions. With the final target, we extract the hidden layers as new features.


## 5.0 Modelling





