from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from datasets import load_dataset, Dataset
import torch
import json

# Step 1: Load your synthetic dataset (JSON)
with open("resource/syrian_arabic_intent_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert to HuggingFace Dataset with input_text and target_text keys
texts = []
for sample in data:
    input_text = sample["utterance"]
    target_text = sample["target"]["response"]
    texts.append({"input_text": input_text, "target_text": target_text})



dataset = Dataset.from_list(texts)

# Optional: split dataset into train/validation
dataset = dataset.train_test_split(test_size=0.1)

# Step 2: Load tokenizer & model
model_name = "UBC-NLP/AraT5v2-base-1024"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print(f"Using device: {device}")    
# Step 3: Tokenize
def preprocess(example):
    inputs = tokenizer(example["input_text"], padding="max_length", truncation=True, max_length=128)
    targets = tokenizer(example["target_text"], padding="max_length", truncation=True, max_length=64)
    inputs["labels"] = targets["input_ids"]
    return inputs

tokenized_train = dataset["train"].map(preprocess, batched=True)
tokenized_eval = dataset["test"].map(preprocess, batched=True)

# Step 4: Training Arguments
training_args = Seq2SeqTrainingArguments(
    output_dir="./resource/arat5_intent_model",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=5,
    logging_steps=50,
    save_steps=500,
    save_total_limit=2,
    evaluation_strategy="steps",
    eval_steps=100,
    fp16=True,  # use if your GPU supports it
    predict_with_generate=True,
    load_best_model_at_end=True,
)

# Step 5: Trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    tokenizer=tokenizer,
    data_collator=DataCollatorForSeq2Seq(tokenizer, model=model)
)

# Train and save
trainer.train()
trainer.save_model("./resource/arat5_intent_model")
