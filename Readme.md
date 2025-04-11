# task to be done
- make following apis
    - summarize
    - brain map
    - summarize history
    - account tracking/monitoring
- add blockchain endpoints
    - ask subash later after above is complete



    run.py


# avilable apis

- `api/authenticate_or_identify` : [POST] -> send a random hash per extention install 
    ```json
    
    ```
- `api/summarize` : [POST] -> send the whole html content, and wait for promise
    -- response
    ```json
    {
        "summary":"text only", -> div-body
        "notes":["text","text"], ->  div>ul>li*
        "refrences":[{"name":"link"}] -> div>li>a>hrefs 
    }
    ```
- `api/fetch_user_history`: [GET] -> responses the D3 friendly json later on, [tommrow]

