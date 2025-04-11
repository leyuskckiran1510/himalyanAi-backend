Here we are going to develop an project related to recall , our second brain where we track user daily activities within browser. It tracks the sumary of user visiting the page and we wil be using AI to summarize his/her visits on the page . The users  info of time interval on certain browse activity is calculated , like user impression and user time on specific page , user learning summary of the page , user also can use chatbot aside to ask for questions and stuffs , like summary of current page . We will be using free trial without login where user session is tracked to for one day timeline of what user did and his summary is tracked as history . 

For premium users we will use IPFS blockchain to store the data and we will be using AI to summarize the data . 



OUR STACK : : 

 CHROME EXTENSION IN JAVASCRIPT <------ API -----> Python flask : { AI summary included } 
                                        |
                                        |
                                        |
                                        |
                                        |
                                        |
                                        +
                                        BlockChain application : 
                                        - Web3 py <----->
                                        - local Node Hardhat(Node) for blockchain 
                                        - chai ,mocha for testing of solidity contract 
                                        - Solidity for userInfo collection .
                                        - IPFS system FileStorage of Blocks in chain



We will be doing blockchain application here : 
1. Python Flask API call will be used to interact with the blockchain application forfile storage stuffs and other onchain query 
2. IPFS will be immplemented for File tracking 



## NEW CHANGES REQUIRED : 

the web3 py will listen for incoming post request 
which includes ['user_addr','summary_content'] 
then it stores that content using IPFS system and generates hash of the summary_content and pyhon  evaluates ['IPFS_HASH','current_data','today_date'{using datetime}','current_time','user_address'] {which later stores inside the } -> [solidity contract ]
solidity contract will have 
address users;
each users will have 
mapping of user_addr => list_of_dates 
each dates will have list of summary of that days , where summaries will be 
{
    'IPFS_HASH' : '0x1234567890',
    'current_time' : '12:00:00',
    'current_date' : '2023-10-01',
}
// These IPFS_HASH , current_time and current_date is calculated using web3 python 
// web3.py include python will have one api endpoint which provides all the data of user history as get_user_history(user_addr) and it returns user history if exists and if no user it should throw error stuffs 