# RELEVANT CODE TO USER

# prompt = st.chat_input("Ask a question or extract policies")

# # Initialize previous_input_type in session_state if it doesn't exist
# if "previous_input_type" not in st.session_state:
#     st.session_state.previous_input_type = None

# # Check if the input type has changed
# if st.session_state.previous_input_type != add_radio:
#     # Clear the messages
#     st.session_state.messages = []
#     # Update previous_input_type
#     st.session_state.previous_input_type = add_radio

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["parts"][0])


# if add_radio == 'Text ✏':
#     model = genai.GenerativeModel(model_name="models/gemini-2.5-pro",
#                                 generation_config=generation_config,
#                                 safety_settings=safety_settings)
#     prompt = st.chat_input("Ask anything")

#     if prompt:
#         message = prompt
#         st.session_state.messages.append({
#             "role":"user",
#             "parts":[message],
#         })
#         with st.chat_message("user"):
#             st.markdown(prompt)
#         response = model.generate_content(st.session_state.messages)
#         with st.chat_message("assistant"):
#             message_placeholder = st.empty()
#             message_placeholder.markdown(response.text)
#         st.session_state.messages.append({
#             "role":"model",
#             "parts":[response.text],
#         })

            

    # send to Gemini
    # st.session_state.messages[{
    #     "role":"user",
    #     "parts":[full_prompt],
    # }]
    # with st.chat_message("user"):
    #     st.markdown(prompt)
    # response = model.generate_content(st.session_state.messages)
    # with st.chat_message("assistant"):
    #     st.markdown(response.text)
    # st.session_state.messages.append({
    #     "role":"model",
    #     "parts":[response.text],
    # })