#include <iostream>
#include <string>

const int INIT_BUFFER_SIZE = 8;
const int GORNER = 127;

template <typename T>
class HashTable {
public:
    HashTable();
    HashTable(int buf_size);
    ~HashTable();
    HashTable(const HashTable& other) = delete;
    HashTable(const HashTable&& other) = delete;
    HashTable& operator=(const HashTable& other) = delete;
    HashTable& operator=(HashTable&& other) = delete;


    bool Add(const T value);
    bool Del(const T value);
    bool Has(const T value);

private:
    T* buffer;
    // bool* del_nodes;

    int buffer_size;
    int size;

    int hash(const std::string value, int size);
    bool is_completed(int buffer_size, int size);
    void resize();
};

template <typename T>
HashTable<T>::HashTable()
{
    buffer = new T[INIT_BUFFER_SIZE];
    // del_nodes = new bool[INIT_BUFFER_SIZE];
    for (int i = 0; i < INIT_BUFFER_SIZE; ++i) {
        buffer[i] = "";
        // del_nodes[i] = false;
    }
    buffer_size = INIT_BUFFER_SIZE;
    size = 0;
}

template <typename T>
HashTable<T>::HashTable(int buf_size)
{
    buffer = new T[buf_size];
    // del_nodes = new bool[buf_size];
    for (int i = 0; i < buf_size; ++i) {
        buffer[i] = "";
        // del_nodes[i] = false;
    }
    buffer_size = buf_size;
    size = 0;
}

template <typename T>
HashTable<T>::~HashTable()
{
    delete[] buffer;
    // delete[] del_nodes;
}

template <typename T>
int HashTable<T>::hash(const std::string value, int buffer_size)
{
    int hash = 0;
    for (int i = 0; i < value.length(); i++) {
        hash = (hash * GORNER + value[i]) % buffer_size;
    }
    return hash;
}

template <typename T>
bool HashTable<T>::is_completed(int buffer_size, int size)
{
    if(4 * size >= 3 * buffer_size)
        return true;
    return false;
}

template <typename T>
bool HashTable<T>::Add(const T value)
{
    if(Has(value))
        return false;
    if(is_completed(buffer_size, size))
        resize();

    size++;

    int key = hash(value, buffer_size);

    int i = 1;
    while(1) {
        if(buffer[key] == "" && buffer[key] == "D") {
            buffer[key] = value;
            // del_nodes[key] = false;
            return true;;
        }
        key = (key + i * i) % buffer_size;
        i++;
    }
}

template <typename T>
bool HashTable<T>::Del(const T value)
{
    if(!Has(value))
        return false;

    size--;

    int key = hash(value, buffer_size);

    int i = 0;
    while(1) {
        if(buffer[key] == value) {
            buffer[key] = "D";
            // del_nodes[key] = true;
            return true;
        }
        key = (key + i * i) % buffer_size;
        i++;
    }
}

template <typename T>
bool HashTable<T>::Has(const T value)
{
    int key = hash(value, buffer_size);

    int i = 0;
    while(1) {
        if(buffer[key] == value)
            return true;
        // if(buffer[key] == "" && del_nodes[key] == false)
            // return false;
        if(i == buffer_size)
            return false;
        key = (key + i * i) % buffer_size;
        i++;
    }
}

template <typename T>
void HashTable<T>::resize()
{
    int new_buffer_size = buffer_size * 2;
    HashTable new_hash_table(new_buffer_size);

    for (int i = 0; i < buffer_size; ++i) {
        new_hash_table.Add(buffer[i]);
    }

    buffer = new T[new_buffer_size];
    // del_nodes = new bool[new_buffer_size];
    for (int i = 0; i < new_buffer_size; ++i) {
        buffer[i] = "";
        // del_nodes[i] = false;
    }

    for (int i = 0; i < new_buffer_size; ++i) {
        buffer[i] = new_hash_table.buffer[i];
        // del_nodes[i] = new_hash_table.del_nodes[i];
    }
    buffer_size = new_buffer_size;
    size = new_hash_table.size;
}

int main()
{
    char command;
    std::string value;

    HashTable<std::string> hash_table;

    while(std::cin >> command >> value) {

        if(command == '+')
            if(hash_table.Add(value))
                std::cout << "OK" << std::endl;
            else
                std::cout << "FAIL" << std::endl;

        if(command == '-')
            if(hash_table.Del(value))
                std::cout << "OK" << std::endl;
            else
                std::cout << "FAIL" << std::endl;

        if(command == '?')
            if(hash_table.Has(value))
                std::cout << "OK" << std::endl;
            else
                std::cout << "FAIL" << std::endl;
    }

    return 0;
}