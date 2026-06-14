import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LassoCV, ElasticNetCV
from sklearn.feature_selection import f_regression, mutual_info_regression, RFE
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import r2_score, root_mean_squared_error

# Load data
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = r"c:\Users\User\Desktop\L6-new-1\50_Startups.csv"
df = pd.read_csv(csv_path)

# Encode states into 3 columns (California, Florida, New York)
df_encoded = df.copy()
df_encoded["State_California"] = (df["State"] == "California").astype(float)
df_encoded["State_Florida"] = (df["State"] == "Florida").astype(float)
df_encoded["State_New York"] = (df["State"] == "New York").astype(float)

features = ["R&D Spend", "Administration", "Marketing Spend", "State_California", "State_Florida", "State_New York"]
X = df_encoded[features]
y = df_encoded["Profit"]

# Train/test split (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# StandardScaler
scaler = StandardScaler()
X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=features)
X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=features)

print("X_train_scaled head:")
print(X_train_scaled.head())

# We want to find the ranking for each of the 10 algorithms
rankings = {}

# Helper to sort features by importance scores
def get_rank(scores_dict, reverse=True):
    sorted_feats = sorted(scores_dict.items(), key=lambda item: item[1], reverse=reverse)
    return [feat for feat, val in sorted_feats]

# 1. Pearson Correlation
pearson_scores = {feat: abs(pearsonr(X_train[feat], y_train)[0]) for feat in features}
rankings["Pearson"] = get_rank(pearson_scores)

# 2. Spearman Correlation
spearman_scores = {feat: abs(spearmanr(X_train[feat], y_train)[0]) for feat in features}
rankings["Spearman"] = get_rank(spearman_scores)

# 3. F-test Regression
f_val, _ = f_regression(X_train_scaled, y_train)
f_scores = {feat: f_val[i] for i, feat in enumerate(features)}
rankings["F-test"] = get_rank(f_scores)

# 4. Mutual Information
mi_val = mutual_info_regression(X_train_scaled, y_train, random_state=42)
mi_scores = {feat: mi_val[i] for i, feat in enumerate(features)}
rankings["Mutual Info"] = get_rank(mi_scores)

# 5. RFE (using Linear Regression)
lr = LinearRegression()
rfe = RFE(estimator=lr, n_features_to_select=1)
rfe.fit(X_train_scaled, y_train)
rfe_ranking = {feat: 10 - rfe.ranking_[i] for i, feat in enumerate(features)}
rankings["RFE"] = get_rank(rfe_ranking)

# 6. SFS Forward
# We can do a manual Forward selection:
# Start with empty set, add the one that gives best CV R2 or train R2.
# Let's write SFS manually:
selected_forward = []
remaining = list(features)
for _ in range(len(features)):
    best_feat = None
    best_score = -np.inf
    for feat in remaining:
        current_test = selected_forward + [feat]
        lr_temp = LinearRegression()
        lr_temp.fit(X_train_scaled[current_test], y_train)
        score = lr_temp.score(X_train_scaled[current_test], y_train)
        if score > best_score:
            best_score = score
            best_feat = feat
    selected_forward.append(best_feat)
    remaining.remove(best_feat)
rankings["SFS"] = selected_forward

# 7. SBS Backward
# Start with all features, remove the one that causes least drop in R2.
selected_backward = list(features)
elimination_order = []
for _ in range(len(features) - 1):
    worst_feat = None
    best_score = -np.inf
    for feat in selected_backward:
        current_test = [f for f in selected_backward if f != feat]
        lr_temp = LinearRegression()
        lr_temp.fit(X_train_scaled[current_test], y_train)
        score = lr_temp.score(X_train_scaled[current_test], y_train)
        if score > best_score:
            best_score = score
            worst_feat = feat
    elimination_order.append(worst_feat)
    selected_backward.remove(worst_feat)
elimination_order.append(selected_backward[0])
rankings["SBS"] = elimination_order[::-1]

# 8. Lasso Penalty
lasso = LassoCV(cv=5, random_state=42).fit(X_train_scaled, y_train)
lasso_scores = {feat: abs(lasso.coef_[i]) for i, feat in enumerate(features)}
rankings["Lasso"] = get_rank(lasso_scores)

# 9. Random Forest
rf = RandomForestRegressor(random_state=42).fit(X_train_scaled, y_train)
rf_scores = {feat: rf.feature_importances_[i] for i, feat in enumerate(features)}
rankings["Random Forest"] = get_rank(rf_scores)

# 10. ElasticNet
enet = ElasticNetCV(l1_ratio=[.1, .5, .7, .9, .95, .99, 1], cv=5, random_state=42).fit(X_train_scaled, y_train)
enet_scores = {feat: abs(enet.coef_[i]) for i, feat in enumerate(features)}
rankings["ElasticNet"] = get_rank(enet_scores)

# Translate rankings to match table values
translation = {
    "R&D Spend": "研發支出",
    "Marketing Spend": "行銷費用",
    "Administration": "行政費用",
    "State_California": "加州",
    "State_Florida": "佛羅里達州",
    "State_New York": "紐約州"
}

print("\n--- Feature Rankings ---")
for name, ranking in rankings.items():
    translated_rank = [translation[feat] for feat in ranking]
    print(f"{name:15}: {', '.join(translated_rank[:5])}")

# Let's evaluate R2 and RMSE for k=1..5 for each algorithm
results = {}
for name, ranking in rankings.items():
    results[name] = {"r2": [], "rmse": []}
    for k in range(1, 6):
        top_k_feats = ranking[:k]
        
        # Fit LinearRegression on top k features
        lr_model = LinearRegression()
        lr_model.fit(X_train_scaled[top_k_feats], y_train)
        
        # Predict on test
        y_pred = lr_model.predict(X_test_scaled[top_k_feats])
        r2 = r2_score(y_test, y_pred)
        rmse = root_mean_squared_error(y_test, y_pred)
        
        results[name]["r2"].append(r2)
        results[name]["rmse"].append(rmse)

print("\n--- R2 Scores for k=1..5 ---")
for name, res in results.items():
    print(f"{name:15}: {', '.join([f'{val:.4f}' for val in res['r2']])}")

print("\n--- RMSE Scores for k=1..5 ---")
for name, res in results.items():
    print(f"{name:15}: {', '.join([f'{val:.2f}' for val in res['rmse']])}")
