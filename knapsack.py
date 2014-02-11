from sr26abbr import load


db = load.load()


orig_target = dict(
    Fiber_TD=38,
    Protein=155,
    Vit_A_RAE=900,
    Vit_C=90,
    Vit_D_mcg=15,
    Vit_E=15,
    Vit_K=120,
    Thiamin=1.2,
    Riboflavin=1.3,
    Niacin=16,
    Vit_B6=1.3,
    Folate_Tot=400,
    Vit_B12=2.4,
    Panto_acid=5,
    # Biotin=30 mcg,
    Choline_Tot=550,
    Calcium=1000,
    Iron=8,
    Magnesium=400,
    Manganese=2.3,
    # Molybdenum = 45 mcg
    Phosphorus=700,
    Potassium=4700,
    Selenium=55,
    Sodium=1500,
    Zinc=11,
    Sugar_Tot=1
    )
max_target = dict(
    Fiber_TD=150,
    Protein=300,
    Vit_A_RAE=3000,
    Vit_C=2000,
    Vit_D_mcg=100,
    Vit_E=1000,
    Niacin=35,
    Vit_B6=100,
    Folate_Tot=1000,
    Choline_Tot=3500,
    Boron=20,
    Calcium=2500,
    Copper=10000,
    Fluoride=10,
    Manganese=11,
    Phosphorus=4000,
    Selenium=400,
    Zinc=40,
    Sodium=2300
    )
optimization_macros = dict(
    Sugar_Tot = -.01,
    Protein = .01,
    Fiber_TD = .02
    )

empty_micros = dict(
    Fiber_TD=0,
    Protein=0,
    Vit_A_RAE=0,
    Vit_C=0,
    Vit_D_mcg=0,
    Vit_E=0,
    Vit_K=0,
    Thiamin=0,
    Riboflavin=0,
    Niacin=0,
    Vit_B6=0,
    Folate_Tot=0,
    Vit_B12=0,
    Panto_acid=0,
    # Biotin=30 mcg,
    Choline_Tot=0,
    Calcium=0,
    Iron=0,
    Magnesium=0,
    Manganese=0,
    # Molybdenum = 45 mcg
    Phosphorus=0,
    Potassium=0,
    Selenium=0,
    Sodium=0,
    Zinc=0,
    Sugar_Tot=0,
    )

#divide nutritient by calorie
def get_db_nuts(target_keys):
    db_nuts = {tkey: {} for tkey in target_keys}
    for key in db.keys():
        cal = db[key]["Energ_Kcal"]
        for tkey in target_keys:
            db_nuts[tkey][key] = (db[key][tkey] / cal
                                  if db[key][tkey] and cal else 0)
    return db_nuts

#sorts nuts by nutrient density
def get_sorted_nuts(db_nuts, target_keys):
    sorted_nuts = dict()
    for tkey in target_keys:
        sorted_nuts[tkey] = sorted(
            db_nuts[tkey].iteritems(), reverse=True, key=lambda x: x[1])
    return sorted_nuts

def get_worst(meal, db_copy, db, target_keys, cur_micros, max_target):
    sorted_nuts = sorted(
        meal, reverse=True, 
        key=lambda x: bad_val(db[x[0]], target_keys, cur_micros, max_target))
    return sorted_nuts[0]

def bad_val(item, target_keys, cur_micros, max_target):
    add_val = 0
    fit_val = 0
    percent_over = 0
    if item["Energ_Kcal"] == 0:
        return 0;
    for tkey in target_keys:
        if (not(item[tkey])):
            continue
        if (not(tkey in max_target)):
            continue
        try:
            percent_over = (cur_micros[tkey]-max_target[tkey])/max_target[tkey]
            percent_over = max(percent_over, 0)
            add_val = percent_over*item[tkey]/max_target[tkey]
            fit_val += add_val
        except:
            fit_val = fit_val
    return fit_val/(item["Energ_Kcal"])
    
def get_best(db_copy, target_keys, cur_micros):
    sorted_nuts = sorted(
db_copy.iteritems(), reverse=True, 
key=lambda x: get_fit_val(x, target_keys, cur_micros))
    return sorted_nuts[0]

name = 0
nut = 0
def get_fit_val(item, target_keys, cur_micros):
    add_val = 0
    fit_val = 0
    percent_off = 0
    percent_over = 0
    if item[1]["Energ_Kcal"] == 0:
        return 0;
    for tkey in target_keys:
        if (not(item[1][tkey])):
            continue
        try:
            percent_off = (orig_target[tkey] - cur_micros[tkey])/orig_target[tkey]
            percent_off = max(percent_off, 0)
            add_val = min(percent_off*item[1][tkey]/orig_target[tkey],percent_off)
            fit_val += max(add_val, 0)
        except:
            fit_val = fit_val
        try:
            percent_over = (cur_micros[tkey]-max_target[tkey])/max_target[tkey]
            percent_over = max(percent_over, 0)
            add_val = percent_over*item[1][tkey]/orig_target[tkey]
            fit_val -= add_val
        except:
            fit_val = fit_val
    for tkey in optimization_macros:
        if (not(item[1][tkey])):
            continue
        try:
            fit_val += item[1][tkey]*optimization_macros[tkey]
        except:
            fit_val = fit_val
    return fit_val/(item[1]["Energ_Kcal"])
    
    
db_copy = db.copy()
target_keys = orig_target.keys()
target = orig_target.copy()
cur_micros = empty_micros.copy()
calories = 0
db_nuts = get_db_nuts(target_keys)
max_calories = 1000
meal = []
def find_answer():
    while True:
        db_copy = db.copy()
        target = orig_target.copy()
        cur_micros = empty_micros.copy()
        calories = 0
        db_nuts = get_db_nuts(target_keys)
        meal = []
        weight = 1
        while calories < max_calories:
            best_food = get_best(db_copy, target_keys, cur_micros)
            meal.append((best_food[0], weight))
            for key in target_keys:
                if (not(db_copy[best_food[0]][key])):
                    continue
                cur_micros[key] = (cur_micros[key] + db_copy[best_food[0]][key] * weight)
            calories += db_copy[best_food[0]]["Energ_Kcal"] * weight
            del db_copy[best_food[0]]
        for x in range(0,10):
            if x > 10:
                x = x
            worst_food = get_worst(meal, db_copy, db, target_keys, cur_micros, max_target)
            meal.remove(worst_food)
            db_copy[worst_food[0]] = db[worst_food[0]]
            worst = db_copy[worst_food[0]]
            for key in target_keys:
                if (not(db_copy[worst_food[0]][key])):
                    continue
                cur_micros[key] = (cur_micros[key] - db_copy[worst_food[0]][key] * weight)
            calories -= db_copy[worst_food[0]]["Energ_Kcal"] * weight
            while calories < max_calories:
                best_food = get_best(db_copy, target_keys, cur_micros)
                meal.append((best_food[0], weight))
                for key in target_keys:
                    if (not(db_copy[best_food[0]][key])):
                        continue
                    cur_micros[key] = (cur_micros[key] + db_copy[best_food[0]][key] * weight)
                calories += db_copy[best_food[0]]["Energ_Kcal"] * weight
                del db_copy[best_food[0]]
            
            
            
        sums = dict(Sugar_Tot=0, FA_Sat=0, Cholestrl=0, Energ_Kcal=0)
        for item, weight in meal:
            if weight:
                print item, "%.2f" % (weight * 100), db[item]["Shrt_Desc"]
            for sum_key in sums.keys():
                if db[item][sum_key]:
                    sums[sum_key] += db[item][sum_key] * weight
        print sums

        keycode = raw_input("Item code to remove: ")
        print "Removing [%s]" % keycode
        if len(keycode) < 5:
            for key in db.keys():
                if key.startswith(keycode):
                    db.pop(key)
        else:
            db.pop(keycode)
        find_answer()    
        
find_answer()
    # rotate thru first to optimize
#    target_keys.append(target_keys.pop(0))