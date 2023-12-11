import numpy as np
from scipy import stats

def DICE_score(preds, gts):
    '''
    Caculate dice scores of tool for each image.
    attributes:
        preds: numpy array with shape: n x w x h,
        gts: numpy array with shape: n x w x h,
                n: number of images, w: width of the image, h: height of the image
                1 for prediction of tool, 0 for prediction of background
    return:
        dice_scores: numpy array with shape n.
    '''
    smooth = 1e-10
    tool_mask = preds >= 0.5
    num = 2 * (tool_mask * gts).sum(axis = (1,2)) + smooth
    denom = (gts.sum(axis = (1,2)) + tool_mask.sum(axis = (1,2))) + smooth
    dice_scores =  num / denom 
    return dice_scores
    

def pairwise_significance(dice_scores_0, dice_scores_1, threshold = 0.05):
    '''
    Caculate the pairwise significance of two set of predictions.
    attributes:
        dice_scores_0: numpy array with shape: n ,
        dice_scores_1: numpy array with shape: n ,
            n: number of images
    return:
        dice_scores: bool value 
            True for significant difference
            False for insignificant difference
    '''
    # do t test and calculate p value, threshold the p_value to see the significance of the difference.
    p_value = stats.ttest_1samp((dice_scores_0 - dice_scores_1) / (dice_scores_0 + dice_scores_1), popmean = 0.0).pvalue
    return p_value <= threshold
    

def ranking_scores(all_preds, gts):
    '''
    Calculate the ranking of predictions and assign scores
    attributes:
        all_preds: list of numpy array with shape: n x w x h, 
                    the length of the list is the number of participants
        gts: numpy array with shape: n x w x h,
    return:
        scores: list of score for participants
    '''
    assert len(all_preds) > 0, "all preds can not be empty"
    # get dice scores for each participants
    all_dice_scores = []
    all_mean_dice_scores = []
    for preds in all_preds:
        dice_scores = DICE_score(preds, gts)
        all_dice_scores.append(dice_scores)
        all_mean_dice_scores.append(dice_scores.mean())
    
    # get initial sort according to the mean dice score
    print(all_mean_dice_scores)
    sort_indices = np.argsort(all_mean_dice_scores)[::-1]
    
    anchor_idx = 0
    scores = [len(sort_indices)]
    for i in range(1, len(sort_indices)):
        if pairwise_significance(dice_scores_0 = all_dice_scores[sort_indices[i]], dice_scores_1 = all_dice_scores[sort_indices[anchor_idx]]):
            # if the comparison is significant comparing to the anchor
            # set score according to the rank
            scores.append(len(sort_indices) - i)
            # set a new anchor
            anchor_idx = i
        else:
            # set the score same to the anchor
            scores.append(scores[anchor_idx])
    
    return scores
