import subprocess

# Question Set
questions = [
    "What is the main function of Solana's proof-of-history mechanism?",
    "What is the consensus mechanism used by Solana, and how does it differ from Ethereum's?",
    "What was Solana's price jump during August 2021?",
    "What is the main purpose of NX finance in Solana ecosystem?",
    "What does the Vault's stake pool in Solana focus on?",
    "How does Solana attempt to solve the blockchain trilemma (scalability, security, decentralization)?",
    "What are some of the key advantages of using Solana over other blockchains like Ethereum and Cardano?",
    "How does Solana maintain decentralization while scaling to high transaction speeds?",
    "What is the significance of the Solana Mobile Stack for the network's future?",
    "What is Solana's approach to improving user experience in blockchain applications?",
    "Why is Solana considered an 'Ethereum killer'?",
    "Based on the Solana network's consensus mechanisms, how might it impact energy consumption compared to Bitcoin or Ethereum's earlier models?",
    "Why might Solana be more attractive for NFT platforms compared to Ethereum?",
    "What potential challenges could Solana face in maintaining decentralization as its network scales?",
    "How does Solana compare to Ethereum in terms of dApp availability and growth?",
    "What is the main difference between Solana's proof-of-history and Bitcoin's proof-of-work?",
    "How do the transaction fees on Solana compare to those on Ethereum?",
    "What differentiates Solana's approach to consensus from traditional proof-of-stake?",
    "When was Solana launched?",
    "What is Solana's token called?",
    "What was the peak value of Solana's token (SOL) in November 2021?",
    "When did Anatoly Yakovenko propose Solana's blockchain?",
    "What is the average transaction throughput (TPS) of Solana according to recent data analysis?",
    "What major vulnerability resulted in the loss of 325 million USD in the Solana ecosystem?",
    "What percentage of Solana's smart contracts are developed using the Anchor framework?",
    "Explain how delegated proof-of-stake works in Solana.",
    "What role do validators play in Solana's blockchain?",
    "What is a validator node in Solana, and what does it do?",
    "How does Solana handle high throughput and scalability in its blockchain?",
    "What is the role of smart contracts in Solana?",
    "What is proof-of-history?",
    "What are the primary components of Solana's network architecture? ",
    "What are Program Derived Addresses (PDAs) in Solana?",
    "What is the significance of Cross-Program Invocations (CPIs) in Solana development?",
    "How can Solana be used in decentralized finance (DeFi)?",
    "What use cases does Solana offer for NFTs?",
    "How does Solana support decentralized finance (DeFi) innovation through platforms like NX Finance?",
    "How can developers leverage Solana for creating high-performance applications?",
    "How does Solana's unique combination of proof-of-history and delegated proof-of-stake contribute to its scalability, and why is this combination considered superior to traditional proof-of-work systems?",
    "What impact did Solana's proof-of-history mechanism have on its ability to address the blockchain trilemma (scalability, security, decentralization), and how does this compare to Ethereum's approach?",
    "Considering Solana's low transaction fees and high throughput, what advantages does it offer for decentralized finance (DeFi) and NFT platforms, and how do these features contrast with Ethereum's higher fees?",
    "How do Solana's transaction confirmation speeds (400ms) benefit decentralized applications (dApps) in the finance and gaming sectors, and what challenges might arise as the network scales?",
    "How does the role of validators in Solana's delegated proof-of-stake system ensure security, and what role does the Vault's community-driven validator selection play in decentralization?",
    "In what ways do Solana's smart contract capabilities (similar to Ethereum) support both decentralized finance (DeFi) and non-fungible tokens (NFTs), and how does Solana's performance in these areas differ from Ethereum's?",
    "How does Solana's approach to validator selection and rewards through NX Finance's leveraging strategies benefit users with varying risk profiles, and what risks might this pose to the network's overall security?",
    "Considering Solana's success in launching the Degenerate Ape Academy and its NFT platform, how might its ecosystem continue to evolve with the introduction of the Solana Mobile Stack, and what implications does this have for user adoption?",
    "How does Solana's approach to consensus mechanisms, particularly the combination of PoH and Proof of Stake (PoS), address the blockchain trilemma of scalability, security, and decentralization?",
    "How does Solana's transaction throughput, as recorded in recent studies, compare to traditional blockchains like Ethereum, and what specific design elements allow Solana to achieve such performance?",
    "Given that Rust is one of the programming languages used to develop Solana smart contracts, how do its features contribute to both the security and challenges faced by developers?",
    "In what ways does Solana address the scalability challenges faced by earlier blockchains like Bitcoin and Ethereum, and what mechanisms ensure that security and decentralization are maintained?",
]

output_file = "output.txt"

# Question Loop
counter = 1
with open(output_file, "w") as f:
    for question in questions:
        command = [
            "python", "-m", "graphrag", "query", 
            "--root", "./projects/Solana", 
            "--method", "drift", 
            "--query", question,
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            f.write(f"Question: {question}\n")
            f.write(f"Answer:\n{result.stdout}\n")
            f.write("="*80 + "\n")
            print(f"Question {counter} Success")
        except subprocess.CalledProcessError as e:
            f.write(f"Error occurred while querying: {question}\n")
            f.write(f"Error message: {e.stderr}\n")
            f.write("="*80 + "\n")
            print(f"---------------------- Question {counter} Fail ----------------------")
        counter += 1
print(f"Results saved to {output_file}")
