class DataManager {
    /*
    This object is passed into the top level app object as an prop
    *hopefully* the stored data can't be modified other than this.writeToStorage method

     */
    constructor(){
        this.storage = {
            // obj are saved as name value tuple pair here
            "game_phase":("loading")
        }
        this.writeToStorage = this.writeToStorage.bind(this)
    }
    writeToStorage(str_name,content){
        const value = content
        this.storage[str_name] = value
    }
}

export default DataManager