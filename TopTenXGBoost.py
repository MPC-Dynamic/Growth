import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_selection import mutual_info_classif
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier  # Import XGBoost classifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, roc_auc_score

# ================================
# PART 1: Read Data, Impute Missing Values, and Compute Mutual Information
# ================================

# Read the original data from all.csv
df = pd.read_csv('all.csv')

# Define the target and non-feature columns.
target_column = 'sat-or-not'
non_feature_columns = [target_column, 'ID']  # add other non-feature columns if needed

# Create a list of predictor columns (features)
predictor_columns = [col for col in df.columns if col not in non_feature_columns]

# Separate predictors (X) and target (y)
X = df[predictor_columns]
y = df[target_column]

# Impute missing values in the predictors using the mean strategy
imputer = SimpleImputer(strategy='mean')
X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

# Compute mutual information scores for each predictor
mi_scores = mutual_info_classif(X_imputed, y, discrete_features='auto', random_state=0)

# Create a DataFrame for feature importances and save it
mi_df = pd.DataFrame({
    'Feature': predictor_columns,
    'Mutual_Information': mi_scores
})
mi_df.to_csv('feature_importance.csv', index=False)
print("Mutual information scores saved to feature_importance.csv")

# ================================
# PART 2: Train a Model and Compute Performance Metrics
# ================================

# Split the imputed data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X_imputed, y, test_size=0.3, random_state=42)

# Train an XGBoost classifier
model = XGBClassifier(
    n_estimators=100,  # Number of trees
    max_depth=5,       # Maximum depth of a tree
    learning_rate=0.1, # Step size shrinkage
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'  # Avoid warnings regarding label encoding
)

model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]  # Probability estimates for the positive class

# Compute performance metrics
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0   # True Positive Rate (Recall)
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0   # True Negative Rate
accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)

# ================================
# PART 3: Visualize Top 10 Features and Annotate Model Performance
# ================================

# Get the top 10 features by MI (highest MI scores) and then sort for horizontal bar chart
mi_df_sorted = mi_df.sort_values(by='Mutual_Information', ascending=False)
top10 = mi_df_sorted.head(10).sort_values(by='Mutual_Information', ascending=True)

plt.figure(figsize=(10, 6))
bars = plt.barh(top10['Feature'], top10['Mutual_Information'], color='skyblue')

# Annotate each bar with its MI value
for bar in bars:
    width = bar.get_width()
    plt.text(width, bar.get_y() + bar.get_height() / 2,
             f'{width:.6f}', va='center', ha='left', fontsize=9)

plt.xlabel("Mutual Information")
plt.title("Top 10 Feature Importances for Predicting 'sat-or-not'")

# Prepare a text block with model performance metrics
metrics_text = (
    f"Model Performance:\n"
    f"Accuracy: {accuracy:.3f}\n"
    f"Sensitivity: {sensitivity:.3f}\n"
    f"Specificity: {specificity:.3f}\n"
    f"AUC: {auc:.3f}"
)

# Add the performance metrics to the plot (adjust coordinates as needed)
plt.figtext(0.75, 0.5, metrics_text, bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 5})

plt.tight_layout()
plt.savefig('top10_feature_importance.png', dpi=300)
print("Visualization saved as top10_feature_importance.png")
plt.show()

# ================================
# PART 4: Append a New Row with MI Scores to the Original Data
# ================================

# Create a dictionary for the MI row: assign the MI value to predictor columns and None to others
mi_row = {}
for col in df.columns:
    if col in predictor_columns:
        mi_value = mi_df.loc[mi_df['Feature'] == col, 'Mutual_Information'].values[0]
        mi_row[col] = mi_value
    else:
        mi_row[col] = None

# Convert the dictionary to a DataFrame row and label the ID
mi_row_df = pd.DataFrame([mi_row])
mi_row_df['ID'] = 'importance_row'

# Append the new MI row to the original DataFrame
df_appended = pd.concat([df, mi_row_df], ignore_index=True)
df_appended.to_csv('all_with_importance.csv', index=False)
print("Original data with appended MI row saved to all_with_importance.csv")
