#!/bin/bash
source ~/.bashrc
conda activate gpt
export CUDA_VISIBLE_DEVICES=0
export OUTPUT=poetry/output_poet
export TRAIN=data/poetry_dry.txt
export VALID=data/poetry_eval.txt
export BS=2
export LR=2e-5

cd /home/u/ru_transformers/
rm $OUTPUT/step.txt
cp ./output_m/config.json $OUTPUT
cp ./output_m/pytorch_model.bin $OUTPUT

for i in {1..6}; do 
    python run_lm_finetuning.py \
        --output_dir=$OUTPUT \
        --model_type=gpt2 \
        --model_name_or_path=$OUTPUT \
        --do_train \
        --train_data_file=$TRAIN \
        --per_gpu_train_batch_size $BS \
        --save_steps=10000 \
        --logging_steps=100 \
        --fp16 \
        --fp16_opt_level O2 \
        --warmup_steps 100 \
        --learning_rate $LR \
        --overwrite_output_dir \
        --tokenizer_class SPEncoder \
        --tokenizer_name bpe/m50.model \
        --lr_decay \
        --do_eval \
        --evaluate_during_training \
        --eval_steps 100 \
        --eval_data_file=$VALID
    sleep 1
done

# 0 2 * * * /home/u/ru_transformers/poetry/train_poet.sh
