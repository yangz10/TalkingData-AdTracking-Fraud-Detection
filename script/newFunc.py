import pandas as pd
import time
import numpy as np
from sklearn.model_selection import train_test_split
import lightgbm as lgb
import gc
import matplotlib.pyplot as plt
import os
import xgboost as xgb

from sklearn.model_selection import train_test_split

from keras.layers import Dense,Dropout
from keras.models import Sequential

def resultGenea(rawData,name='Day_6',epochs=2):
    rawData_day_6 = rawData
    features = featureMonitor(rawData_day_6, name, saveT=False,testSet=rawData_day_6,
                            batch_size=512, ifTrain=False, epochs=epochs)
    bst = xgb.Booster(model_file=(name+'_xgb_'+'.model'))
    xgbMatirx = xgb.DMatrix(features.values)
    preData = bst.predict(xgbMatirx)
    rawData_day_6['result'] = preData
    finalData = pd.Series(rawData_day_6['result'])
    return finalData

def trainingPipeline(rawData, epochs, name='Day_6'):
    rawData_day_6 = rawData
    features = featureMonitor(rawData=rawData, Day_name=name, saveT=True, ifTrain=True,
                              testSet=rawData, batch_size=512, epochs=epochs)
    target = rawData_day_6['is_attributed']
    X_tra, X_val, y_tra, y_val = train_test_split(features, target, test_size=0.4, random_state=92)
    xgb_params = {'eta': 0.05,
                  'max_depth': 100,
                  'n_estimators': 1400,
                  'silent': False,
                  'objective': 'binary:logistic',
                  'eval_metric': 'auc',
                  'nthread': 2,
                  'njobs': -1,
                  'gamma': 5.103973694670875e-08,
                  'max_delta_step': 20,
                  'min_child_weight': 4,
                  'subsample': 0.7,
                  'colsample_bylevel': 0.1,
                  'colsample_bytree': 0.7,
                  'reg_alpha': 1e-09,
                  'reg_lambda': 10.0,
                  'scale_pos_weight': 499.99999999999994,
                  'random_state': 84,
                  ' tree_method': 'approx'
                  }

    xgtrain = xgb.DMatrix(X_tra.values, label=y_tra.values)
    xgvalid = xgb.DMatrix(X_val.values, label=y_val.values)
    gc.collect()

    watchlist = [(xgtrain, 'train'), (xgvalid, 'test')]
    num_round = 3000
    bst = xgb.train(xgb_params, xgtrain, num_round, watchlist, maximize=True, early_stopping_rounds=100, verbose_eval=5)
    bst.save_model(name + '_xgb_' + '.model')

def featureMonitor(rawData, Day_name, saveT, testSet, batch_size, epochs,ifTrain):
    col = ['ip', 'app', 'device', 'os', 'channel', 'hour', 'minute', 'second']
    rawData_day_6 = rawData

    rawData_day_6_next_click = do_next_Click(rawData_day_6)
    rawData_day_6_prev_Click = do_prev_Click(rawData_day_6)
    rawData_day_6_cumCount = cumCount(rawData_day_6)
    rawData_day_6_count = countFeature(rawData_day_6)
    rawData_day_6_var = varFeature(rawData_day_6)
    rawData_day_6_mean = meanFeature(rawData_day_6)
    rawData_day_6_unique = uniqueFeature(rawData_day_6)
    originalFeature = rawData_day_6[col]
    if ifTrain :
        target = rawData_day_6['is_attributed'].values
    else :
        target = ''

    Features_1 = modelTrain(rawData_day_6_next_click, target, Day_name + '_1', rawData_day_6_next_click, saveT=saveT,
                            batch_size=batch_size, epochs=epochs,ifTrain=ifTrain)
    Features_2 = modelTrain(rawData_day_6_prev_Click, target, Day_name + '_2', rawData_day_6_prev_Click, saveT=saveT,
                            batch_size=batch_size, epochs=epochs,ifTrain=ifTrain)
    Features_3 = modelTrain(rawData_day_6_cumCount, target, Day_name + '_3', rawData_day_6_cumCount, saveT=saveT,
                            batch_size=batch_size, epochs=epochs,ifTrain=ifTrain)
    Features_4 = modelTrain(rawData_day_6_count, target, Day_name + '_4', rawData_day_6_count, saveT=saveT,
                            batch_size=batch_size, epochs=epochs,ifTrain=ifTrain)
    Features_5 = modelTrain(rawData_day_6_var, target, Day_name + '_5', rawData_day_6_var, saveT=saveT,
                            batch_size=batch_size, epochs=epochs,ifTrain=ifTrain)
    Features_6 = modelTrain(rawData_day_6_mean, target, Day_name + '_6', rawData_day_6_mean, saveT=saveT,
                            batch_size=batch_size, epochs=epochs,ifTrain=ifTrain)
    Features_7 = modelTrain(rawData_day_6_unique, target, Day_name + '_7', rawData_day_6_unique, saveT=saveT,
                            batch_size=batch_size, epochs=epochs,ifTrain=ifTrain)
    Features_8 = modelTrain(originalFeature, target, Day_name + '_8', originalFeature, saveT=saveT,
                            batch_size=batch_size, epochs=epochs,ifTrain=ifTrain)
    featureList = [Features_1, Features_2, Features_3, Features_4, Features_5, Features_6, Features_7,
                   Features_8,originalFeature]
    trueIndex = originalFeature.index
    pdList = []
    for m in featureList:
        m = pd.DataFrame(m)
        m.index = trueIndex
        pdList.append(m)
    allFeature = pd.concat(pdList, axis=1,ignore_index=True)
    return allFeature

def modelTrain(originalFeature, target, name, predValue, saveT=True,
                ifTrain=True, batch_size=512, epochs=20):

    model = Sequential()

    model.add(Dense(50, input_shape=(originalFeature.shape[1],)))
    model.add(Dense(100, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(500, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(10, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation="relu"))
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    # model.summary()
    if ifTrain :
        X_tra, X_val, y_tra, y_val = train_test_split(originalFeature, target, test_size=0.4, random_state=42)
        hist = model.fit(X_tra, y_tra, batch_size=batch_size, epochs=epochs, validation_data=(X_val, y_val), verbose=1)
        print('-'*400)

    name = str(name) + '.h5'

    if saveT:
        model.save_weights(name)
    else:
        model.load_weights(name)

    if predValue.shape[1] != originalFeature.shape[1]:
        print('check !!!!')
        print(predValue.shape)
        print(originalFeature.shape)


    model.pop()
    model.pop()
    # model.summary()
    output = model.predict(predValue, batch_size=batch_size, verbose=1)
    return output

def splitDataDay(rawData):
    rawData_time = timeFeature(rawData)
    rawData_day_6 = rawData_time[rawData_time['day'] == 6]
    rawData_day_7 = rawData_time[rawData_time['day'] == 7]
    rawData_day_8 = rawData_time[rawData_time['day'] == 8]
    rawData_day_9 = rawData_time[rawData_time['day'] == 9]
    return rawData_day_6,rawData_day_7,rawData_day_8,rawData_day_9

def timeFeature(X_train,var='click_time'):
    X_train['day'] = X_train[var].dt.day.astype('uint8')
    X_train['hour'] = X_train[var].dt.hour.astype('uint8')
    X_train['minute'] = X_train[var].dt.minute.astype('uint8')
    X_train['second'] = X_train[var].dt.second.astype('uint8')
    return X_train

def do_next_Click(df, agg_suffix='nextClick', agg_type='float32'):
    # print(f">> \nExtracting {agg_suffix} time calculation features...\n")

    GROUP_BY_NEXT_CLICKS = [

        # V1
        {'groupby': ['ip']},
        {'groupby': ['ip', 'app']},
        {'groupby': ['ip', 'channel']},
        {'groupby': ['ip', 'os']},

        # V3
        {'groupby': ['ip', 'app', 'device', 'os', 'channel']},
        {'groupby': ['ip', 'os', 'device']},
        {'groupby': ['ip', 'os', 'device', 'app']},
        {'groupby': ['device']},
        {'groupby': ['device', 'channel']},
        {'groupby': ['app', 'device', 'channel']},
        {'groupby': ['device', 'hour']}
    ]

    # Calculate the time to next click for each group
    for spec in GROUP_BY_NEXT_CLICKS:
        # Name of new feature
        new_feature = '{}_{}'.format('_'.join(spec['groupby']), agg_suffix)

        # Unique list of features to select
        all_features = spec['groupby'] + ['click_time']

        # Run calculation
        # print(f">> Grouping by {spec['groupby']}, and saving time to {agg_suffix} in: {new_feature}")
        df[new_feature] = (df[all_features].groupby(spec['groupby']).click_time.shift(-1) - df.click_time).dt.seconds.astype(agg_type)
        gc.collect()
    df = df.fillna(-99)
    return (df.iloc[:,12:])

def do_prev_Click(df, agg_suffix='prevClick', agg_type='float32'):
    # print(f">> \nExtracting {agg_suffix} time calculation features...\n")

    GROUP_BY_NEXT_CLICKS = [

        # V1
        {'groupby': ['ip']},
        {'groupby': ['ip', 'app']},
        {'groupby': ['ip', 'channel']},
        {'groupby': ['ip', 'os']},

        # V3
        {'groupby': ['ip', 'app', 'device', 'os', 'channel']},
        {'groupby': ['ip', 'os', 'device']},
        {'groupby': ['ip', 'os', 'device', 'app']}
    ]

    # Calculate the time to next click for each group
    for spec in GROUP_BY_NEXT_CLICKS:
        # Name of new feature
        new_feature = '{}_{}'.format('_'.join(spec['groupby']), agg_suffix)

        # Unique list of features to select
        all_features = spec['groupby'] + ['click_time']

        # Run calculation
        # print(f">> Grouping by {spec['groupby']}, and saving time to {agg_suffix} in: {new_feature}")
        df[new_feature] = (df.click_time - df[all_features].groupby(spec[
                                                                        'groupby']).click_time.shift(
            +1)).dt.seconds.astype(agg_type)
        gc.collect()
        df = df.fillna(-99)
    return (df.iloc[:,12:])

## Below a function is written to extract count feature by aggregating different cols
def do_count(df, group_cols, agg_type='uint16', show_max=False, show_agg=True):
    agg_name = '{}count'.format('_'.join(group_cols))
    if show_agg:
        print("\nAggregating by ", group_cols, '... and saved in', agg_name)
    gp = df[group_cols][group_cols].groupby(group_cols).size().rename(agg_name).to_frame().reset_index()
    df = df.merge(gp, on=group_cols, how='left')
    del gp
    if show_max:
        print(agg_name + " max value = ", df[agg_name].max())
    df[agg_name] = df[agg_name].astype(agg_type)
    #     print('predictors',predictors)
    gc.collect()
    return (df.iloc[:,12:])

##  Below a function is written to extract unique count feature from different cols
def do_countuniq(df, group_cols, counted, agg_type='uint8', show_max=False, show_agg=True):
    agg_name = '{}_by_{}_countuniq'.format(('_'.join(group_cols)), (counted))
    if show_agg:
        print("\nCounting unqiue ", counted, " by ", group_cols, '... and saved in', agg_name)
    gp = df[group_cols + [counted]].groupby(group_cols)[counted].nunique().reset_index().rename(
        columns={counted: agg_name})
    df = df.merge(gp, on=group_cols, how='left')
    del gp
    if show_max:
        print(agg_name + " max value = ", df[agg_name].max())
    df[agg_name] = df[agg_name].astype(agg_type)
    #     print('predictors',predictors)
    gc.collect()

    return (df.iloc[:,12:])

### Below a function is written to extract cumulative count feature  from different cols
def do_cumcount(df, group_cols, counted, agg_type='uint16', show_max=False, show_agg=True):
    agg_name = '{}_by_{}_cumcount'.format(('_'.join(group_cols)), (counted))
    if show_agg:
        print("\nCumulative count by ", group_cols, '... and saved in', agg_name)
    gp = df[group_cols + [counted]].groupby(group_cols)[counted].cumcount()
    df[agg_name] = gp.values
    del gp
    if show_max:
        print(agg_name + " max value = ", df[agg_name].max())
    df[agg_name] = df[agg_name].astype(agg_type)
    #     print('predictors',predictors)
    gc.collect()

    return (df.iloc[:,12:])

### Below a function is written to extract mean feature  from different cols
def do_mean(df, group_cols, counted, agg_type='float16', show_max=False, show_agg=True):
    agg_name = '{}_by_{}_mean'.format(('_'.join(group_cols)), (counted))
    if show_agg:
        print("\nCalculating mean of ", counted, " by ", group_cols, '... and saved in', agg_name)
    gp = df[group_cols + [counted]].groupby(group_cols)[counted].mean().reset_index().rename(
        columns={counted: agg_name})
    df = df.merge(gp, on=group_cols, how='left')
    del gp
    if show_max:
        print(agg_name + " max value = ", df[agg_name].max())
    df[agg_name] = df[agg_name].astype(agg_type)
    #     print('predictors',predictors)
    gc.collect()
    return (df.iloc[:,12:])

def do_var(df, group_cols, counted, agg_type='float16', show_max=False, show_agg=True):
    agg_name = '{}_by_{}_var'.format(('_'.join(group_cols)), (counted))
    if show_agg:
        print("\nCalculating variance of ", counted, " by ", group_cols, '... and saved in', agg_name)
    gp = df[group_cols + [counted]].groupby(group_cols)[counted].var().reset_index().rename(columns={counted: agg_name})
    df = df.merge(gp, on=group_cols, how='left')
    del gp
    if show_max:
        print(agg_name + " max value = ", df[agg_name].max())
    df[agg_name] = df[agg_name].astype(agg_type)
    #     print('predictors',predictors)
    gc.collect()

    return (df.iloc[:,12:])


def cumCount(train_df):
    train_df_1 = do_cumcount(train_df, ['ip'], 'os');
    gc.collect()
    train_df_2 = do_cumcount(train_df, ['ip', 'device', 'os'], 'app');
    gc.collect()
    dfList = [train_df_1, train_df_2]
    data = pd.concat(dfList, axis=1)
    data = data.fillna(-99999)

    return data


def countFeature(train_df):
    train_df_1 = do_count(train_df, ['ip', 'day', 'hour']);
    gc.collect()
    train_df_2 = do_count(train_df, ['ip', 'app']);
    gc.collect()
    train_df_3 = do_count(train_df, ['ip', 'app', 'os']);
    gc.collect()
    dfList = [train_df_1, train_df_2, train_df_3]
    data = pd.concat(dfList, axis=1)
    data = data.fillna(-99)

    return data


def varFeature(train_df):
    train_df_1 = do_var(train_df, ['ip', 'day', 'channel'], 'hour');
    gc.collect()
    train_df_2 = do_var(train_df, ['ip', 'app', 'os'], 'hour');
    gc.collect()
    train_df_3 = do_var(train_df, ['ip', 'app', 'channel'], 'day');
    gc.collect()
    dfList = [train_df_1, train_df_2, train_df_3]
    data = pd.concat(dfList, axis=1)
    data = data.fillna(-99)

    return data


def meanFeature(train_df):
    train_df = do_mean(train_df, ['ip', 'app', 'channel'], 'hour');
    gc.collect()
    train_df = train_df.fillna(-99)

    return train_df

def uniqueFeature(rawData_day_6):

    train_df_1 = do_countuniq( rawData_day_6, ['ip'], 'channel' ); gc.collect()
    train_df_2 = do_countuniq( rawData_day_6, ['ip'], 'channel' ); gc.collect()
    train_df_3 = do_countuniq( rawData_day_6, ['ip', 'device', 'os'], 'app'); gc.collect()
    train_df_4 = do_countuniq( rawData_day_6, ['ip', 'day'], 'hour' ); gc.collect()
    train_df_5 = do_countuniq( rawData_day_6, ['ip'], 'app'); gc.collect()
    train_df_6 = do_countuniq( rawData_day_6, ['ip', 'app'], 'os'); gc.collect()
    train_df_7 = do_countuniq( rawData_day_6, ['ip'], 'device'); gc.collect()
    train_df_8 = do_countuniq( rawData_day_6, ['app'], 'channel'); gc.collect()
    dfList = [train_df_1,train_df_2,train_df_3,train_df_4,train_df_5,train_df_6,train_df_7,train_df_8]
    data = pd.concat(dfList,axis=1)
    data = data.fillna(-99)
    return data
