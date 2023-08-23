def store_temp_subs(user_sub):
    temp_subs = {}
    temp_subs['Basic'] = user_sub.Basic
    temp_subs['Basic_Expiration'] = user_sub.Basic_Expiration
    temp_subs['Premium'] = user_sub.Premium
    temp_subs['Premium_Expiration'] = user_sub.Premium_Expiration
    return temp_subs

def store_temp_data(user_data):
    temp_data = {}
    temp_data["budget"] = user_data.budget
    temp_data["bundle"] = user_data.bundle
    temp_data["media"] = user_data.media
    return temp_data