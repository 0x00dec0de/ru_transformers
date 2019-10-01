#!/bin/bash
source ~/.bashrc
conda activate gpt
export CUDA_VISIBLE_DEVICES=0
cd /home/u/ru_transformers/poetry/
cp ../output_m/config.json output_poet/
cp ../output_m/pytorch_model.bin output_poet/
cd ..
for i in {1..40}; do 
    python run_lm_finetuning.py \
        --output_dir=poetry/output_poet \
        --model_type=gpt2 \
        --model_name_or_path=poetry/output_poet \
        --do_train \
        --train_data_file=data/poetry_dry.txt \
        --per_gpu_train_batch_size=3 \
        --save_steps=10000 \
        --logging_steps=1 \
        --fp16 \
        --fp16_opt_level O2 \
        --warmup_steps 100 \
        --learning_rate 3e-5 \
        --overwrite_output_dir \
        --tokenizer_class SPEncoder \
        --tokenizer_name bpe/m50.model \
        --lr_decay
    sleep 1
done

# 0 2 * * * /home/u/ru_transformers/poetry/train_poet.sh
