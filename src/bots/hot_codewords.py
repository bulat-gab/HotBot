CRYPTO_EXPLORE_TASKS = {
    "What is Crypto airdops"                                                   : "free",
    "What is Meme coins"                                                       : "hype",
    "What is Crypto swaps"                                                     : "commissions",
    "What is Airdrop in Crypto and How Does it Work?"                          : "discover",
    "Blockchain Ecosystem"                                                     : "community",
    "Crypto Tokens Explained — Utility and Security Tokens, NFTs, Memecoins"   : "explore and learn",
    "Four Types of Blockchain Explained"                                       : "try island hopping",
    "Beginners guide HOT Wallet"                                               : "seed phrase",
    "What is Blockchain"                                                       : "smart contracts",
    "How to spend HOT from balance?"                                           : "hot mining",
    "Who is Market Makers"                                                     : "profit",
}


OTHER_TASKS = {
    "What is TON Blockchain"                                                   : "fast",
    "What is Solana Blockchain"                                                : "marketplace"
}

def get_codeword(text: str) -> str:
    if not text:
        return ""
    
    for k, v in CRYPTO_EXPLORE_TASKS.items():
        if k in text:
            return v
    
    return ""
    

def get_first_line(input: str) -> str:
    if not input:
        return ""
    
    return input.split('\n')[0]