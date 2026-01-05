from memory_lib import Memory, chat_with_memories, init_clients


def main():
    openai_client, tidb_client, embedding_fn = init_clients()
    memory = Memory(tidb_client, embedding_fn, openai_client)

    print("Memory chat (type 'exit' to quit)")
    user_id = input("User ID (default_user): ").strip() or "default_user"

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        print(f"AI: {chat_with_memories(user_input, memory, openai_client, user_id=user_id)}")


if __name__ == "__main__":
    main()
