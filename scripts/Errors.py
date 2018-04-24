# -*- coding: utf-8 -*-

# This method stores error messages
# When an error code is submited, the correspondent message is returned
# errcode: error code
def gen_msg_error(errcode):

    if errcode == 'ERR_001':
        return 'Imagem desfocada ou com baixa qualidade.'

    elif errcode == 'ERR_002':
        return 'Imagem muito escura.'

    elif errcode == 'ERR_003':
        return 'Não foi possível detectar o círculo central.'

    elif errcode == 'ERR_004':
        return 'A imagem apresenta sombras ou alguma outra coisa que possa atrapalhar o reconhecimento dos ovos.'
    
    elif errcode == 'ERR_005':
        return 'Bordas da paleta não encontradas.'

    elif errcode == 'ERR_006':
        return 'Bordas da paleta e círculo central não encontrados.'
    
    elif errcode == 'ERR_007':
        return 'Foram encontradas marcas d\'água na imagem.'
    
    elif errcode == 'ERR_008':
        return 'Imagem com baixa resolução.'

    elif errcode == 'ERR_009':
        return 'Paleta não reconhecida.'

    elif errcode == 'ERR_010':
        return 'Enquadramento da paleta inadequado.'

    elif errcode == 'ERR_011':
        return 'Fundo da imagem escuro.'