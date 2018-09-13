import React from "react"

import MainPlayerField from "./mainPlayerField"
import MainUtilityBar from "./mainUtilityBar"

class Main extends React.Component{
    /*
    props:
    - ws_manager
    - match_state
    - game_state

    children:
    - player field (homemade carousel component)
        - match_state
        - game_state
    - main utility bar
        - ws_manager
        - game_state
        - match_state
    */
    constructor(props){
        super(props)
    }
    render(){
        return(
            <div className={"full_screen_component"}>
                <MainPlayerField match_state={this.props.match_state} game_state={this.props.game_state}/>
                <MainUtilityBar match_state={this.props.match_state} ws_manager={this.props.ws_manager}/>
            </div>
        )
    }
}

export default Main