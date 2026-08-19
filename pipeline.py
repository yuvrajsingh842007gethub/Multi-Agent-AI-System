from agents import build_reader_agent , build_search_agent , writer_chain , critic_chain

def run_research_pipeline(topic:str) -> dict:
    state = {}

    # step=1 search_agent working
    print("\n"+"="*50)
    print("step 1 = search agent are working.....")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    
    # --- YAHAN CHANGE HAI: Raw content nikalne ke liye ---
    raw_content = search_result['messages'][-1].content
    
    # Agar content list/dictionary format me hai, to use clean text banayein
    if isinstance(raw_content, list):
        clean_text = ""
        for block in raw_content:
            if isinstance(block, dict) and block.get("type") == "text":
                clean_text += block.get("text", "") + "\n"
        state["search_results"] = clean_text.strip()
    else:
        state["search_results"] = str(raw_content)

    print("\nsearch result:", state["search_results"])




    #step=2 search_agent working
    print("\n"+"="*50)
    print("step 2 = Reader agent is scaraping top resources.....")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
        f"Based on the following search results about '{topic}', "
        f"pick the most relevant URL and scrape it for deeper content.\n\n"
        f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content
    print("\n scaraped result:",state['scraped_content'])



    # step 3. writer chain
    print("\n"+"="*50)
    print("step 3 = Writer is draftting report.....")
    print("="*50)

    research_combine = (
        f"SEARCH RESULT: \n {state ['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT: \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combine
    })
    print("\nFinal report ", state["report"])


    #critic report 
    print("\n"+"="*50)
    print("step 4 =  critic is reviewing the reoprt.....")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print(f"/n Critic report: /n",state["feedback"])

    return state

if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)

    