def clear_residue_tokens():
    from auth_prime.models import Token_Table
    from datetime import datetime

    now = datetime.now()

    old_token_ref = Token_Table.objects.all().order_by("-token_id")[:10]
    c = True

    while(c == True):
        for token in old_token_ref:
            flag = False
            dt_end_ref = datetime.strptime(token.token_end, '%d-%m-%y %H:%M:%S')
            if(now > dt_end_ref):
                token.delete()
                flag = True
            
            if(flag == False):
                c = False
                break
        
        del(old_token_ref)
        old_token_ref = Token_Table.objects.all().order_by("-token_id")[:10]

    print("[.] Overdue tokens cleared.")