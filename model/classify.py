# model/classify.py - CUDA 충돌 해결 버전
import torch
import os
import pickle
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from config import MODEL_PATH  # 예: "/home/.../results3"

# ───────────────────────────────────────────────────────
# 전역 변수로 모델 캐시 (지연 로딩용)
# ───────────────────────────────────────────────────────
_model_cache = None
_tokenizer_cache = None
_label_encoder_cache = None
_device_cache = None

def get_classify_components():
    """모델, 토크나이저, 라벨 인코더를 지연 로딩으로 반환"""
    global _model_cache, _tokenizer_cache, _label_encoder_cache, _device_cache
    
    if _model_cache is None:
        print("🔄 BERT 분류 모델 로딩 중...")
        
        # 1) 디바이스 결정
        _device_cache = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"💻 BERT classify device: {_device_cache}")
        
        # 2) 토크나이저 로드
        _tokenizer_cache = AutoTokenizer.from_pretrained(
            MODEL_PATH, 
            local_files_only=True
        )
        
        # 3) 모델 로드
        _model_cache = (
            AutoModelForSequenceClassification
            .from_pretrained(MODEL_PATH, local_files_only=True)
            .eval()
            .to(_device_cache)
        )
        
        # 4) 라벨 인코더 로드
        with open(os.path.join(MODEL_PATH, "label_encoder.pkl"), "rb") as f:
            _label_encoder_cache = pickle.load(f)
            
        print("✅ BERT 분류 모델 로딩 완료!")
    
    return _model_cache, _tokenizer_cache, _label_encoder_cache, _device_cache

# ───────────────────────────────────────────────────────
# 분류 함수 (지연 로딩 적용)
# ───────────────────────────────────────────────────────
def predict_category(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return "기타"
    
    try:
        # 모델 컴포넌트 가져오기 (첫 호출시에만 로딩)
        model, tokenizer, label_encoder, device = get_classify_components()
        
        # 토크나이징
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=256
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # 추론
        with torch.no_grad():
            logits = model(**inputs).logits
        
        pred_id = torch.argmax(logits, 1).item()
        category = label_encoder.inverse_transform([pred_id])[0]
        
        return category
        
    except Exception as e:
        print(f"❌ BERT 분류 중 오류 발생: {e}")
        return "기타"

# ───────────────────────────────────────────────────────
# 선택사항: CPU 전용 모드
# ───────────────────────────────────────────────────────
def predict_category_cpu_only(text: str) -> str:
    """CPU 전용으로 분류 (CUDA 문제 완전 회피)"""
    global _model_cache, _tokenizer_cache, _label_encoder_cache
    
    if not isinstance(text, str) or not text.strip():
        return "기타"
    
    try:
        if _model_cache is None:
            print("🔄 BERT 분류 모델 로딩 중 (CPU 전용)...")
            
            # CPU로 강제 설정
            device = torch.device("cpu")
            
            _tokenizer_cache = AutoTokenizer.from_pretrained(
                MODEL_PATH, 
                local_files_only=True
            )
            
            _model_cache = (
                AutoModelForSequenceClassification
                .from_pretrained(MODEL_PATH, local_files_only=True)
                .eval()
                .to(device)  # CPU로 강제
            )
            
            with open(os.path.join(MODEL_PATH, "label_encoder.pkl"), "rb") as f:
                _label_encoder_cache = pickle.load(f)
                
            print("✅ BERT 분류 모델 로딩 완료 (CPU)!")
        
        inputs = _tokenizer_cache(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=256
        )
        # CPU이므로 .to() 필요 없음
        
        with torch.no_grad():
            logits = _model_cache(**inputs).logits
        
        pred_id = torch.argmax(logits, 1).item()
        return _label_encoder_cache.inverse_transform([pred_id])[0]
        
    except Exception as e:
        print(f"❌ BERT 분류 중 오류 발생: {e}")
        return "기타"