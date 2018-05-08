FILENO = 7  # To distinguish the output file name.
debug = 0  # Whethere or not in debuging mode
import pandas as pd
import time
import numpy as np
from sklearn.model_selection import train_test_split
import lightgbm as lgb
import gc
import matplotlib.pyplot as plt
import os

###### Feature extraction ######

#### Extracting next click feature
### Taken help from https://www.kaggle.com/nanomathias/feature-engineering-importance-testing
###Did some Cosmetic changes
predictors = []





###  A function is written to train the lightGBM model with different given parameters
if debug:
    print('*** debug parameter set: this is a test run for debugging purposes ***')


def lgb_modelfit_nocv(params, dtrain, dvalid, predictors, target='target', objective='binary', metrics='auc',
                      feval=None, early_stopping_rounds=50, num_boost_round=3000, verbose_eval=10,
                      categorical_features=None):
    lgb_params = {
        'boosting_type': 'gbdt',
        'objective': objective,
        'metric': metrics,
        'learning_rate': 0.05,
        # 'is_unbalance': 'true',  #because training data is unbalance (replaced with scale_pos_weight)
        'num_leaves': 31,  # we should let it be smaller than 2^(max_depth)
        'max_depth': -1,  # -1 means no limit
        'min_child_samples': 20,  # Minimum number of data need in a child(min_data_in_leaf)
        'max_bin': 255,  # Number of bucketed bin for feature values
        'subsample': 0.6,  # Subsample ratio of the training instance.
        'subsample_freq': 0,  # frequence of subsample, <=0 means no enable
        'colsample_bytree': 0.3,  # Subsample ratio of columns when constructing each tree.
        'min_child_weight': 5,  # Minimum sum of instance weight(hessian) needed in a child(leaf)
        'subsample_for_bin': 200000,  # Number of samples for constructing bin
        'min_split_gain': 0,  # lambda_l1, lambda_l2 and min_gain_to_split to regularization
        'reg_alpha': 0,  # L1 regularization term on weights
        'reg_lambda': 0,  # L2 regularization term on weights
        'nthread': 8,
        'verbose': 0,
    }

    lgb_params.update(params)

    print("preparing validation datasets")

    xgtrain = lgb.Dataset(dtrain[predictors].values, label=dtrain[target].values,
                          feature_name=predictors,
                          categorical_feature=categorical_features
                          )
    xgvalid = lgb.Dataset(dvalid[predictors].values, label=dvalid[target].values,
                          feature_name=predictors,
                          categorical_feature=categorical_features
                          )
    del dtrain
    del dvalid
    gc.collect()

    evals_results = {}

    bst1 = lgb.train(lgb_params,
                     xgtrain,
                     valid_sets=[xgvalid],
                     valid_names=['valid'],
                     evals_result=evals_results,
                     num_boost_round=num_boost_round,
                     early_stopping_rounds=early_stopping_rounds,
                     verbose_eval=10,
                     feval=feval)

    print("\nModel Report")
    print("bst1.best_iteration: ", bst1.best_iteration)
    print(metrics + ":", evals_results['valid'][metrics][bst1.best_iteration - 1])

    return (bst1, bst1.best_iteration)


## Running the full calculation.

#### A function is written here to run the full calculation with defined parameters.

def DO(frm, to, fileno):
    dtypes = {
        'ip': 'uint32',
        'app': 'uint16',
        'device': 'uint8',
        'os': 'uint16',
        'channel': 'uint16',
        'is_attributed': 'uint8',
        'click_id': 'uint32',
    }

    print('loading train data...', frm, to)
    train_df = pd.read_csv("../input/train.csv", parse_dates=['click_time'], skiprows=range(1, frm), nrows=to - frm,
                           dtype=dtypes,
                           usecols=['ip', 'app', 'device', 'os', 'channel', 'click_time', 'is_attributed'])

    print('loading test data...')
    if debug:
        test_df = pd.read_csv("../input/test.csv", nrows=100000, parse_dates=['click_time'], dtype=dtypes,
                              usecols=['ip', 'app', 'device', 'os', 'channel', 'click_time', 'click_id'])
    else:
        test_df = pd.read_csv("../input/test.csv", parse_dates=['click_time'], dtype=dtypes,
                              usecols=['ip', 'app', 'device', 'os', 'channel', 'click_time', 'click_id'])

    len_train = len(train_df)
    train_df = train_df.append(test_df)

    del test_df

    gc.collect()
    train_df['hour'] = pd.to_datetime(train_df.click_time).dt.hour.astype('int8')
    train_df['day'] = pd.to_datetime(train_df.click_time).dt.day.astype('int8')
    train_df = do_next_Click(train_df, agg_suffix='nextClick', agg_type='float32');
    gc.collect()
    train_df = do_prev_Click(train_df, agg_suffix='prevClick', agg_type='float32');
    gc.collect()  ## Removed temporarily due RAM sortage.

    train_df = do_countuniq(train_df, ['ip'], 'channel');
    gc.collect()
    train_df = do_countuniq(train_df, ['ip', 'device', 'os'], 'app');
    gc.collect()
    train_df = do_countuniq(train_df, ['ip', 'day'], 'hour');
    gc.collect()
    train_df = do_countuniq(train_df, ['ip'], 'app');
    gc.collect()
    train_df = do_countuniq(train_df, ['ip', 'app'], 'os');
    gc.collect()
    train_df = do_countuniq(train_df, ['ip'], 'device');
    gc.collect()
    train_df = do_countuniq(train_df, ['app'], 'channel');
    gc.collect()
    train_df = do_cumcount(train_df, ['ip'], 'os');
    gc.collect()
    train_df = do_cumcount(train_df, ['ip', 'device', 'os'], 'app');
    gc.collect()
    train_df = do_count(train_df, ['ip', 'day', 'hour']);
    gc.collect()
    train_df = do_count(train_df, ['ip', 'app']);
    gc.collect()
    train_df = do_count(train_df, ['ip', 'app', 'os']);
    gc.collect()
    # train_df = do_var( train_df, ['ip', 'day', 'channel'], 'hour'); gc.collect()
    # train_df = do_var( train_df, ['ip', 'app', 'os'], 'hour'); gc.collect()
    # train_df = do_var( train_df, ['ip', 'app', 'channel'], 'day'); gc.collect()
    # train_df = do_mean( train_df, ['ip', 'app', 'channel'], 'hour' ); gc.collect()

    del train_df['day']
    gc.collect()
    gc.collect()

    print('\n\nBefore appending predictors...\n\n', sorted(predictors))
    target = 'is_attributed'
    word = ['app', 'device', 'os', 'channel', 'hour']
    for feature in word:
        if feature not in predictors:
            predictors.append(feature)
    categorical = ['app', 'device', 'os', 'channel', 'hour']
    print('\n\nAfter appending predictors...\n\n', sorted(predictors))

    test_df = train_df[len_train:]
    val_df = train_df[(len_train - val_size):len_train]
    train_df = train_df[:(len_train - val_size)]

    print("\ntrain size: ", len(train_df))
    print("\nvalid size: ", len(val_df))
    print("\ntest size : ", len(test_df))

    sub = pd.DataFrame()
    sub['click_id'] = test_df['click_id'].astype('int')

    gc.collect()

    print("Training...")
    start_time = time.time()

    params = {
        'learning_rate': 0.10,
        # 'is_unbalance': 'true', # replaced with scale_pos_weight argument
        'num_leaves': 7,  # 2^max_depth - 1
        'max_depth': 3,  # -1 means no limit
        'min_child_samples': 100,  # Minimum number of data need in a child(min_data_in_leaf)
        'max_bin': 100,  # Number of bucketed bin for feature values
        'subsample': 0.7,  # Subsample ratio of the training instance.
        'subsample_freq': 1,  # frequence of subsample, <=0 means no enable
        'colsample_bytree': 0.9,  # Subsample ratio of columns when constructing each tree.
        'min_child_weight': 0,  # Minimum sum of instance weight(hessian) needed in a child(leaf)
        'scale_pos_weight': 200  # because training data is extremely unbalanced
    }
    (bst, best_iteration) = lgb_modelfit_nocv(params,
                                              train_df,
                                              val_df,
                                              predictors,
                                              target,
                                              objective='binary',
                                              metrics='auc',
                                              early_stopping_rounds=30,
                                              verbose_eval=True,
                                              num_boost_round=1000,
                                              categorical_features=categorical)

    print('[{}]: model training time'.format(time.time() - start_time))
    del train_df
    del val_df
    gc.collect()

    ax = lgb.plot_importance(bst, max_num_features=300)

    plt.savefig('test%d.png' % (fileno), dpi=600, bbox_inches="tight")
    plt.show()

    print("Predicting...")
    sub['is_attributed'] = bst.predict(test_df[predictors], num_iteration=best_iteration)
    #     if not debug:
    #         print("writing...")
    sub.to_csv('sub_it%d.csv' % (fileno), index=False, float_format='%.9f')
    print("done...")
    return sub


####### Chunk size defining and final run  ############

nrows = 184903891 - 1
nchunk = 25000000
val_size = 2500000

frm = nrows - 65000000
if debug:
    frm = 0
    nchunk = 100000
    val_size = 10000

to = frm + nchunk

sub = DO(frm, to, FILENO)