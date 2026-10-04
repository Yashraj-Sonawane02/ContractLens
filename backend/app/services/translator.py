import os
import json
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Try importing google genai SDK
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

HINDI_LEGAL_DICTIONARY = {
    "Unlawful threat to cut off or disconnect essential water, electricity, or utility supplies.": {
        "reason": "आवश्यक पानी, बिजली या जनसुविधा आपूर्ति काटने या रोकने की गैर-कानूनी धमकी।",
        "legal_explanation": "महाराष्ट्र किराया नियंत्रण अधिनियम 1999 की धारा 29 मकान मालिकों को किसी भी परिस्थिति में, किराया बकाया होने पर भी, पानी, बिजली या आवश्यक सेवाएं काटने या रोकने से सख्ती से प्रतिबंधित करती है।",
        "simple_explanation": "यह शर्त विवाद होने पर आपकी बिजली या पानी काटने की धमकी देती है। महाराष्ट्र में आवश्यक सुविधाएं काटना सख्त गैर-कानूनी है।",
        "recommendation": "सुविधा कटौती से संबंधित सभी संदर्भों को तुरंत हटाएं।"
    },
    "Unlawful total waiver of court access and unilateral sole arbitrator appointment.": {
        "reason": "कोर्ट जाने के अधिकार का पूर्ण त्याग और एकतरफा मध्यस्थ की नियुक्ति कानूनन अमान्य है।",
        "legal_explanation": "भारतीय अनुबंध अधिनियम 1872 की धारा 28 के तहत अदालती अधिकार सीमित करने वाले करार शून्य होते हैं। एकतरफा मध्यस्थ की नियुक्ति उच्चतम न्यायालय के फैसलों के अनुसार गैर-कानूनी है।",
        "simple_explanation": "यह शर्त आपको अदालत जाने से रोकती है और मकान मालिक को अपना जज चुनने देती है। भारतीय कानून में यह पूरी तरह अमान्य है।",
        "recommendation": "इसे पारस्परिक मध्यस्थता या सिविल कोर्ट अधिकार क्षेत्र से बदलें।"
    },
    "Illegal self-help eviction, changing locks, or unannounced entry without court process.": {
        "reason": "बिना अदालती आदेश के ताले बदलना, गैर-कानूनी बेदखली या बिना सूचना के घर में प्रवेश।",
        "legal_explanation": "महाराष्ट्र किराया नियंत्रण अधिनियम धारा 15 व 24 और संपत्ति अंतरण अधिनियम धारा 108 के तहत कानूनी प्रक्रिया अनिवार्य है। मकान मालिक खुद ताले नहीं बदल सकते।",
        "simple_explanation": "मकान मालिक बिना नोटिस ताला बदलने या जबरन निकालने का दावा कर रहा है। कानून में जबरन बेदखली प्रतिबंधित है।",
        "recommendation": "कम से कम 48 घंटे की अग्रिम लिखित सूचना और कानूनी प्रक्रिया अनिवार्य करें।"
    },
    "Severe violation of privacy rights via bedroom surveillance or coerced personal data sharing.": {
        "reason": "बेडरूम में सीसीटीवी कैमरे या व्यक्तिगत डेटा जबरन साझा करने से निजता के अधिकार का उल्लंघन।",
        "legal_explanation": "निजी आवासीय क्षेत्रों में सीसीटीवी या व्यक्तिगत वित्तीय डेटा साझा करने का दबाव संविधान के अनुच्छेद 21 (निजता का अधिकार) और DPDP अधिनियम 2023 का उल्लंघन है।",
        "simple_explanation": "यह शर्त बेडरूम में कैमरे लगाने या बैंक विवरण साझा करने के लिए मजबूर करती है। यह आपकी निजता का गंभीर उल्लंघन है।",
        "recommendation": "निजी क्षेत्रों में कैमरे लगाने की शर्त तुरंत हटाएं।"
    },
    "Forfeiture of full security deposit for minor lifestyle or technical infractions.": {
        "reason": "छोटे-मोटे कारणों (पेट्स, दीवार पर कील, भोजन) के लिए पूरी सुरक्षा जमा राशि जब्त करना गैर-कानूनी जुर्माना है।",
        "legal_explanation": "भारतीय अनुबंध अधिनियम 1872 की धारा 74 के तहत छोटे कारणों से पूरा डिपॉजिट जब्त करना एक गैर-कानूनी जुर्माना है। अदालत केवल वास्तविक नुकसान की ही भरपाई की अनुमति देती है।",
        "simple_explanation": "छोटे कारणों जैसे दीवार पर फोटो लगाने पर पूरा पैसा जब्त करने की धमकी दी गई है। कानून में यह अवैध है।",
        "recommendation": "छोटे कारणों पर डिपॉजिट जब्ती की शर्त हटाएं।"
    },
    "Extremely high daily penalty fine or exorbitant interest rate on delayed payments.": {
        "reason": "किराया देरी पर अत्यधिक दैनिक जुर्माना (₹500+/दिन) या अत्यधिक ब्याज दर (12%+)।",
        "legal_explanation": "भारतीय अनुबंध अधिनियम धारा 74 के तहत अत्यधिक दैनिक जुर्माना या भारी ब्याज गैर-कानूनी है। केवल वास्तविक नुकसान का उचित मुआवजा दिया जा सकता है।",
        "simple_explanation": "किराया में थोड़ी देरी पर भारी रोज का जुर्माना लगाया गया है। भारतीय कानून में अत्यधिक जुर्माना लगाना मना है।",
        "recommendation": "ब्याज दर को अधिकतम 10% वार्षिक तक सीमित करें और दैनिक जुर्माना हटाएं।"
    },
    "Total security deposit forfeiture and heavy penalty during lock-in period exit.": {
        "reason": "लॉक-इन अवधि के दौरान जल्दी निकलने पर पूरी सुरक्षा जमा राशि जब्त करना गैर-कानूनी है।",
        "legal_explanation": "धारा 74 के तहत बिना वास्तविक नुकसान साबित किए 100% डिपॉजिट जब्त करना अत्यधिक जुर्माना माना जाता है।",
        "simple_explanation": "लॉक-इन में जल्दी खाली करने पर पूरा डिपॉजिट रखने की बात कही गई है। मकान मालिक केवल नए किरायेदार मिलने तक का वास्तविक नुकसान ही काट सकता है।",
        "recommendation": "क्षतिपूर्ति को अधिकतम 1 महीने के किराये तक सीमित करें।"
    },
    "Unilateral rent escalation or unnegotiated rent increase during tenure.": {
        "reason": "किरायेदार की सहमति के बिना एकतरफा किराया बढ़ाना (महाराष्ट्र किराया नियंत्रण अधिनियम धारा 10/11 के तहत सीमित)।",
        "legal_explanation": "महाराष्ट्र किराया नियंत्रण अधिनियम 1999 की धारा 10 व 11 के तहत वार्षिक किराया वृद्धि 4% पर सीमित है।",
        "simple_explanation": "मकान मालिक कभी भी संदेश भेजकर किराया बढ़ाने का दावा कर रहा है। महाराष्ट्र में किराया वृद्धि कानूनन सीमित है।",
        "recommendation": "नवीनीकरण पर अधिकतम 5% की पारस्परिक किराया वृद्धि तय करें।"
    },
    "Severe notice period imbalance restricting tenant termination rights.": {
        "reason": "असममित नोटिस अवधि (किरायेदार के लिए 3 महीने, मकान मालिक के लिए केवल 7 दिन)।",
        "legal_explanation": "किरायेदार से 3 महीने और मालिक को 7 दिन की नोटिस की छूट देना संपत्ति अंतरण अधिनियम की धारा 106 व 108 के विपरीत है।",
        "simple_explanation": "आपको खाली करने के लिए 3 महीने का नोटिस देना होगा, पर मालिक आपको 7 दिन में निकाल सकता है। यह नोटिस अवधि बहुत असंतुलित है।",
        "recommendation": "दोनों पक्षों के लिए 30 दिनों की समान नोटिस अवधि तय करें।"
    },
    "Standard routine contractual covenant adhering to standard legal practice.": {
        "reason": "मानक कानूनी प्रथाओं के अनुरूप सामान्य दिनचर्या संविदात्मक शर्त।",
        "legal_explanation": "यह प्रावधान संपत्ति अंतरण अधिनियम 1882 और महाराष्ट्र लीव एंड लाइसेंस मानकों के तहत प्रथागत कानूनी अधिकारों के अनुरूप है।",
        "simple_explanation": "यह संतुलित लीज करारों में पाई जाने वाली एक मानक और सामान्य शर्त है।",
        "recommendation": "किसी कार्रवाई की आवश्यकता नहीं है। शर्त संतुलित है।"
    }
}

MARATHI_LEGAL_DICTIONARY = {
    "Unlawful threat to cut off or disconnect essential water, electricity, or utility supplies.": {
        "reason": "पाणी, वीज किंवा आवश्यक सुविधा खंडित करण्याची बेकायदेशीर धमकी (महाराष्ट्र भाडे नियंत्रण कायदा १९९९ कलम २९).",
        "legal_explanation": "महाराष्ट्र भाडे नियंत्रण कायदा १९९९ चे कलम २९ मकान मालकाला कोणत्याही परिस्थितीत (भाडे थकले तरीही) पाणी, वीज किंवा आवश्यक सुविधा खंडित करण्यास सक्त मनाई करते.",
        "simple_explanation": "हा करार वाद झाल्यास तुमची वीज किंवा पाणी तोडण्याची धमकी देतो. महाराष्ट्रात आवश्यक सुविधा बंद करणे पूर्णपणे बेकायदेशीर आहे.",
        "recommendation": "सुविधा खंडित करण्यासंबंधीच्या सर्व अटी करारातून काढून टाका."
    },
    "Unlawful total waiver of court access and unilateral sole arbitrator appointment.": {
        "reason": "न्यायालयात जाण्याचा अधिकार सोडणे व एकतर्फी मध्यस्थ नियुक्त करणे कायद्यानुसार बेकायदेशीर आहे.",
        "legal_explanation": "भारतीय करार कायदा १८७२ कलम २८ व २३ नुसार न्यायालयाचा मार्ग रोखणाऱ्या अटी शून्य ठरतात. एकतर्फी मध्यस्थ नियुक्ती सर्वोच्च न्यायालयाच्या निवाड्यानुसार बेकायदेशीर आहे.",
        "simple_explanation": "ही अट तुम्हाला कोर्टात जाण्यापासून रोखते आणि मालकाला स्वतःचा मध्यस्थ निवडण्याची परवानगी देते. भारतीय कायद्यानुसार हे शून्य आहे.",
        "recommendation": "परस्पर संमतीने मध्यस्थ किंवा दिवाणी न्यायालयाचे अधिकार क्षेत्र निश्चित करा."
    },
    "Illegal self-help eviction, changing locks, or unannounced entry without court process.": {
        "reason": "कोर्टाच्या आदेशाशिवाय कुलूप बदलणे, जबरदस्तीने बाहेर काढणे किंवा न सांगता घरात प्रवेश करणे.",
        "legal_explanation": "महाराष्ट्र भाडे नियंत्रण कायदा कलम १५ व २४ आणि मालमत्ता हस्तांतरण कायदा कलम १०८ नुसार कायदेशीर प्रक्रियेशिवाय जबरदस्तीने ताबा घेणे बेकायदेशीर आहे.",
        "simple_explanation": "घरमालक नोटीस न देता कुलूप बदलण्याचा किंवा बाहेर काढण्याचा दावा करत आहे. कायद्यानुसार न्यायालयात गेल्याशिवाय बाहेर काढता येत नाही.",
        "recommendation": "कमित कमी ४८ तासांची पूर्वसुचना आणि कायदेशीर प्रक्रिया अनिवार्य करा."
    },
    "Severe violation of privacy rights via bedroom surveillance or coerced personal data sharing.": {
        "reason": "बेडरूममध्ये सीसीटीव्ही किंवा वैयक्तिक माहिती सक्तीने देणे हे गोपनीयतेच्या हक्काचे उल्लंघन आहे.",
        "legal_explanation": "खाजगी बेडरूममध्ये कॅमेरे लावणे किंवा वैयक्तिक आर्थिक माहिती सक्तीने मागणे हे कलम २१ अंतर्गत गोपनीयतेच्या मूलभूत हक्काचे उल्लंघन आहे.",
        "simple_explanation": "ही अट बेडरूममध्ये कॅमेरे लावण्याची किंवा बँक माहिती सक्तीने घेण्याची परवानगी देते. हा गोपनीयतेच्या हक्काचा भंग आहे.",
        "recommendation": "खाजगी जागेतील कॅमेरे व डेटा सक्तीची अट काढून टाका."
    },
    "Forfeiture of full security deposit for minor lifestyle or technical infractions.": {
        "reason": "छोट्या कारणांसाठी (प्राणी, भिंतीवरील खिळे) संपूर्ण डिपॉझिट जप्त करणे बेकायदेशीर आहे.",
        "legal_explanation": "भारतीय करार कायदा १८७२ कलम ७४ नुसार भिंतीवर खिळा मारणे किंवा प्राण्यांमुळे संपूर्ण डिपॉझिट जप्त करणे हा अवाजवी दंड असून तो बेकायदेशीर ठरतो.",
        "simple_explanation": "भिंतीवर खिळा मारल्यास सर्व डिपॉझिट जप्त करण्याची धमकी दिली आहे. कायद्यात ही अट अमान्य आहे.",
        "recommendation": "किरकोळ कारणांसाठी डिपॉझिट जप्तीची अट रद्द करा."
    },
    "Extremely high daily penalty fine or exorbitant interest rate on delayed payments.": {
        "reason": "भाडे विलंबासाठी रोजचा प्रचंड दंड (₹५००+/दिवस) किंवा अवाजवी व्याज (१२%+).",
        "legal_explanation": "भारतीय करार कायदा कलम ७४ नुसार अवाजवी रोजचा दंड किंवा प्रचंड व्याजदर बेकायदेशीर मानला जातो. न्यायालय फक्त प्रत्यक्ष नुकसानीचीच भरपाई मंजूर करते.",
        "simple_explanation": "भाडे देण्यास उशीर झाल्यास रोजचा मोठा दंड आकारला आहे. कायद्यानुसार अवाजवी दंड वसूल करता येत नाही.",
        "recommendation": "व्याजाचा दर वर्षाला कमाल १०% पर्यंत मर्यादित करा व दैनंदिन दंड रद्द करा."
    },
    "Total security deposit forfeiture and heavy penalty during lock-in period exit.": {
        "reason": "लॉक-इन कालावधीत बाहेर पडल्यास पूर्ण डिपॉझिट जप्त करणे बेकायदेशीर आहे.",
        "legal_explanation": "कलम ७४ नुसार प्रत्यक्ष भाडे नुकसान सिद्ध केल्याशिवाय संपूर्ण डिपॉझिट जप्त करणे कायदेशीररीत्या अमान्य आहे.",
        "simple_explanation": "लॉक-इन कालावधीत जागा सोडल्यास पूर्ण डिपॉझिट जप्त करण्याची अट आहे. मालक फक्त नवीन भाडेकरू मिळेपर्यंतचे प्रत्यक्ष नुकसान कापून उर्वरित रक्कम परत करेल.",
        "recommendation": "नुकसानभरपाई कमाल १ महिन्याच्या भाड्यापुरती मर्यादित करा."
    },
    "Unilateral rent escalation or unnegotiated rent increase during tenure.": {
        "reason": "एकतर्फी भाडेवाढ करणे (महाराष्ट्र भाडे नियंत्रण कायदा कलम १० व ११ नुसार नियंत्रित).",
        "legal_explanation": "महाराष्ट्र भाडे नियंत्रण कायदा १९९९ कलम ११ नुसार वार्षिक भाडेवाढ कमाल ४% पर्यंतच वैध आहे.",
        "simple_explanation": "घरमालक कधीही मेसेज करून भाडे वाढवण्याचा दावा करत आहे. महाराष्ट्रात भाडेवाढ नियमांनुसारच होऊ शकते.",
        "recommendation": "नूतनीकरणाच्या वेळी परस्पर संमतीने कमाल ५% भाडेवाढ निश्चित करा."
    },
    "Severe notice period imbalance restricting tenant termination rights.": {
        "reason": "असममित नोटीस कालावधी (भाडेकरूसाठी ९० दिवस, मालकासाठी फक्त ७ दिवस).",
        "legal_explanation": "भाडेकरूसाठी ९० दिवस आणि मालकासाठी फक्त ७ दिवसांची नोटीस ही अट मालमत्ता हस्तांतरण कायदा कलम १०६ च्या विरोधी आहे.",
        "simple_explanation": "तुम्हाला जागा सोडण्यासाठी ३ महिन्यांची नोटीस द्यावी लागेल, पण मालक ७ दिवसांत बाहेर काढू शकतो. हा नोटीस कालावधी अत्यंत अन्यायी आहे.",
        "recommendation": "दोन्ही पक्षांसाठी ३० दिवसांची समान नोटीस मुदत निश्चित करा."
    },
    "Standard routine contractual covenant adhering to standard legal practice.": {
        "reason": "मानक कायदेशीर पद्धतींनुसार सामान्य भाडेकरार अट.",
        "legal_explanation": "ही अट मालमत्ता हस्तांतरण कायदा १८८२ व महाराष्ट्र लिव्ह अँड लायसन्स मानकांनुसार कायदेशीररीत्या सुसंगत आहे.",
        "simple_explanation": "ही संतुलित भाडेकरारात आढळणारी एक सर्वसामान्य आणि मानक अट आहे.",
        "recommendation": "कोणत्याही कारवाईची गरज नाही. अट संतुलित आहे."
    }
}

STATUTE_TRANSLATIONS = {
    "Hindi": {
        "Maharashtra Rent Control Act, 1999": "महाराष्ट्र किराया नियंत्रण अधिनियम, 1999",
        "Transfer of Property Act, 1882": "संपत्ति अंतरण अधिनियम, 1882",
        "Indian Contract Act, 1872": "भारतीय अनुबंध अधिनियम, 1872",
        "Section 7": "धारा 7", "Section 10": "धारा 10", "Section 11": "धारा 11",
        "Section 14": "धारा 14", "Section 15": "धारा 15", "Section 16": "धारा 16",
        "Section 24": "धारा 24", "Section 29": "धारा 29", "Section 55": "धारा 55",
        "Section 105": "धारा 105", "Section 106": "धारा 106", "Section 108": "धारा 108",
        "Section 111": "धारा 111", "Section 23": "धारा 23", "Section 28": "धारा 28", "Section 74": "धारा 74"
    },
    "Marathi": {
        "Maharashtra Rent Control Act, 1999": "महाराष्ट्र भाडे नियंत्रण कायदा, १९९९",
        "Transfer of Property Act, 1882": "मालमत्ता हस्तांतरण कायदा, १८८२",
        "Indian Contract Act, 1872": "भारतीय करार कायदा, १८७२",
        "Section 7": "कलम ७", "Section 10": "कलम १०", "Section 11": "कलम ११",
        "Section 14": "कलम १४", "Section 15": "कलम १५", "Section 16": "कलम १६",
        "Section 24": "कलम २४", "Section 29": "कलम २९", "Section 55": "कलम ५५",
        "Section 105": "कलम १०५", "Section 106": "कलम १०६", "Section 108": "कलम १०८",
        "Section 111": "कलम १११", "Section 23": "कलम २३", "Section 28": "कलम २८", "Section 74": "कलम ७४"
    }
}

STATUTE_TITLE_TRANSLATIONS = {
    "Hindi": {
        "Section 7": "परिभाषाएं — लाइसेंसधारक, लाइसेंसदाता, मानक किराया, किरायेदार",
        "Section 10": "मानक किराए से अधिक किराया अवैध",
        "Section 11": "वार्षिक किराया वृद्धि और सुधारों के लिए वृद्धि",
        "Section 14": "पगड़ी या अत्यधिक जमा राशि मांगने पर रोक",
        "Section 15": "मानक किराया देने पर बेदखली नहीं की जा सकती",
        "Section 16": "मकान मालिक कब्जा कब वापस पा सकता है (बेदखली के आधार)",
        "Section 24": "अवधि समाप्त होने पर लाइसेंस परिसर का कब्जा वापस पाने का अधिकार",
        "Section 29": "पानी, बिजली या आवश्यक सेवाएं बंद करने पर रोक",
        "Section 55": "किराया समझौता लिखित और पंजीकृत होना अनिवार्य",
        "Section 105": "पट्टे की परिभाषा",
        "Section 106": "करार के अभाव में नोटिस अवधि (15 दिन की नोटिस)",
        "Section 108": "पट्टाकर्ता और पट्टेदार के अधिकार और दायित्व",
        "Section 111": "पट्टे की समाप्ति",
        "Section 10 (ICA)": "कौन से समझौते अनुबंध हैं — स्वतंत्र सहमति और वैध उद्देश्य",
        "Section 23": "कौन से उद्देश्य वैध हैं और कौन से नहीं",
        "Section 28": "कानूनी कार्यवाही पर रोक लगाने वाले समझौते शून्य",
        "Section 74": "अनुबंध के उल्लंघन पर जुर्माने की भरपाई"
    },
    "Marathi": {
        "Section 7": "व्याख्या — परवानाधारक, परवानादाता, मानक भाडे, भाडेकरू",
        "Section 10": "मानक भाड्यापेक्षा जास्त भाडे बेकायदेशीर",
        "Section 11": "वार्षिक भाडेवाढ व सुधारणांसाठी भाडेवाढ",
        "Section 14": "पगडी किंवा अवाजवी डिपॉझिट मागण्यास मनाई",
        "Section 15": "मानक भाडे भरल्यास बेदखली करता येत नाही",
        "Section 16": "मकान मालक ताबा कधी मिळवू शकतो (बेदखलीची कारणे)",
        "Section 24": "मुदत संपल्यानंतर लिव्ह अँड लायसन्स जागेचा ताबा मिळवण्याचा अधिकार",
        "Section 29": "पाणी, वीज किंवा आवश्यक सुविधा बंद करण्यास मनाई",
        "Section 55": "भाडेकरार लेखी व नोंदणीकृत असणे सक्तीचे",
        "Section 105": "भाडेपट्ट्याची व्याख्या",
        "Section 106": "कराराच्या अभावी नोटीस कालावधी (१५ दिवस नोटीस)",
        "Section 108": "घरमालक व भाडेकरूचे अधिकार आणि जबाबदाऱ्या",
        "Section 111": "भाडेपट्टयाची समाप्ती",
        "Section 10 (ICA)": "कोणते करार वैध असतात — मुक्त संमती व कायदेशीर उद्देश",
        "Section 23": "कोणते उद्देश कायदेशीर किंवा बेकायदेशीर आहेत",
        "Section 28": "न्यायालयीन प्रक्रियेस रोखणारे करार शून्य",
        "Section 74": "कराराचा भंग झाल्यास अवाजवी दंडाबाबत भरपाई"
    }
}

def translate_clause_analysis(clause_analysis: Dict[str, Any], target_language: str) -> Dict[str, Any]:
    if not target_language or target_language.lower() == "english":
        return clause_analysis

    lang = target_language.strip().capitalize()
    is_hindi = "hind" in lang.lower()
    is_marathi = "marath" in lang.lower()

    translated_clause = dict(clause_analysis)
    orig_reason = clause_analysis.get("reason", "")
    gemini_success = False

    # 1. Try Gemini AI Translation if API key is present
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or getattr(settings, "GEMINI_API_KEY", "").strip()
    if HAS_GENAI and api_key and len(api_key) > 15 and "your_" not in api_key.lower():
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
Translate the following legal clause evaluation completely into {lang}.
Ensure all legal explanations, findings, plain-language summaries, recommendations, and statutory takeaways are fluently translated in formal legal {lang}.

Input JSON:
{json.dumps({
    "reason": clause_analysis.get("reason", ""),
    "legal_explanation": clause_analysis.get("legal_explanation", ""),
    "simple_explanation": clause_analysis.get("simple_explanation", ""),
    "recommendation": clause_analysis.get("recommendation", ""),
    "suggested_wording": clause_analysis.get("suggested_wording", "")
}, ensure_ascii=False)}

Return JSON matching the exact keys translated into {lang}.
"""
            models_to_try = ["gemini-flash-latest", "gemini-3.6-flash", "gemini-3.5-flash"]
            response = None
            for m_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    if response and response.text:
                        break
                except Exception as ex:
                    logger.warning(f"Translation model {m_name} failed: {ex}")
                    continue
            if response and response.text:
                translated = json.loads(response.text)
                if translated.get("reason") and translated.get("legal_explanation"):
                    translated_clause["reason"] = translated["reason"]
                    translated_clause["legal_explanation"] = translated["legal_explanation"]
                    translated_clause["simple_explanation"] = translated.get("simple_explanation", clause_analysis.get("simple_explanation"))
                    translated_clause["recommendation"] = translated.get("recommendation", clause_analysis.get("recommendation"))
                    if translated.get("suggested_wording"):
                        translated_clause["suggested_wording"] = translated.get("suggested_wording")
                    gemini_success = True
        except Exception as e:
            logger.warning(f"Gemini translation fallback to statutory legal dictionary: {e}")

    # 2. Deterministic Legal Dictionary Translation Fallback
    if not gemini_success:
        dict_map = HINDI_LEGAL_DICTIONARY if is_hindi else MARATHI_LEGAL_DICTIONARY if is_marathi else {}
        if orig_reason in dict_map:
            entry = dict_map[orig_reason]
            translated_clause["reason"] = entry["reason"]
            translated_clause["legal_explanation"] = entry["legal_explanation"]
            translated_clause["simple_explanation"] = entry["simple_explanation"]
            translated_clause["recommendation"] = entry["recommendation"]

    # 3. Translate Statutory Authority & Precedent Citations completely
    rel_statutes = clause_analysis.get("relevant_statutes", [])
    if rel_statutes:
        translated_statutes = []
        stat_map = STATUTE_TRANSLATIONS.get("Hindi" if is_hindi else "Marathi", {})
        title_map = STATUTE_TITLE_TRANSLATIONS.get("Hindi" if is_hindi else "Marathi", {})

        for stat in rel_statutes:
            s_copy = dict(stat)
            act_orig = stat.get("act_name", "")
            sec_orig = stat.get("section", "")

            if act_orig in stat_map:
                s_copy["act_name"] = stat_map[act_orig]
            if sec_orig in stat_map:
                s_copy["section"] = stat_map[sec_orig]

            if sec_orig in title_map:
                s_copy["title"] = title_map[sec_orig]

            # Translate takeaways
            if "Section 29" in sec_orig or "29" in sec_orig:
                s_copy["key_legal_takeaway"] = "मकान मालकाला भाडेकरूची वीज, पाणी किंवा आवश्यक सुविधा खंडित करण्यास सक्त मनाई आहे (कलम २९)." if is_marathi else "मकान मालिक को किरायेदार की बिजली, पानी या आवश्यक सेवाएं रोकने पर सख्त प्रतिबंध है (धारा 29)।"
            elif "Section 28" in sec_orig or "28" in sec_orig:
                s_copy["key_legal_takeaway"] = "अदालती हक्क सोडणे किंवा एकतर्फी मध्यस्थ नियुक्त करणे कायद्यानुसार शून्य व बेकायदेशीर आहे." if is_marathi else "अदालती अधिकार छोड़ना या एकतरफा मध्यस्थ की नियुक्ति कानूनन अमान्य एवं शून्य है।"
            elif "Section 24" in sec_orig or "24" in sec_orig:
                s_copy["key_legal_takeaway"] = "परवान्याची मुदत संपल्यास ताबा देणे सक्तीचे आहे. कायदेशीर प्रक्रियेशिवाय ताबा घेणे गैर-कायदेशीर आहे." if is_marathi else "लाइसेंस समाप्त होने पर कब्जा देना अनिवार्य है। बिना अदालती प्रक्रिया के कब्जा लेना गैर-कानूनी है।"
            elif "Section 74" in sec_orig or "74" in sec_orig:
                s_copy["key_legal_takeaway"] = "अवाजवी दैनंदिन दंड किंवा संपूर्ण डिपॉझिट जप्ती बेकायदेशीर आहे. न्यायालय केवळ प्रत्यक्ष झालेल्या नुकसानीचीच भरपाई मंजूर करते." if is_marathi else "अत्यधिक दैनिक जुर्माना या पूरी सुरक्षा जमा राशि की जब्ती गैर-कानूनी है। केवल वास्तविक नुकसान का मुआवजा ही मान्य है।"
            elif "Section 11" in sec_orig or "11" in sec_orig:
                s_copy["key_legal_takeaway"] = "वार्षिक भाडेवाढ कमाल ४% पर्यंत मर्यादित आहे. एकतर्फी भाडेवाढ बेकायदेशीर आहे." if is_marathi else "वार्षिक किराया वृद्धि अधिकतम 4% तक सीमित है। एकतरफा किराया वृद्धि गैर-कानूनी है।"
            elif "Section 7" in sec_orig or "7" in sec_orig:
                s_copy["key_legal_takeaway"] = "भाडेकरू (कायदेशीर हक्क असलेला) व परवानाधारक (मर्यादित वापर हक्क असलेला) यांच्यातील कायदेशीर फरक स्पष्ट करतो." if is_marathi else "किरायेदार (कानूनी अधिकार) और लाइसेंसधारक (सीमित उपयोग अधिकार) के बीच कानूनी अंतर स्पष्ट करता है।"
            elif "Section 15" in sec_orig or "15" in sec_orig:
                s_copy["key_legal_takeaway"] = "भाडेकरूने भाडे भरल्यास त्याला बेकायदेशीरपणे बाहेर काढण्यापासून संरक्षण मिळते." if is_marathi else "किरायेदार द्वारा किराया देने पर उसे मनमाने ढंग से बेदखल होने से सुरक्षा मिलती है।"

            translated_statutes.append(s_copy)
        translated_clause["relevant_statutes"] = translated_statutes

    return translated_clause
