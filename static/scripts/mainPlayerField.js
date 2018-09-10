import React from "react"

import EmoBar from "./emoBar"
import SomePlayerMain from "./somePlayerMain"


class MainPlayerField extends React.Component{
    /*
    This component also has the controls needed to cycle through the carousel
    props:
    - match_state
    - game_state

    children:
    - emoFaceBar
        props:
            displayed_player
            match_state
    - someMainPlayer
        props:
            player = game_state.players[num]
    */
    constructor(props){
        super(props)
        this.state = {
            "displayed_player": 0 // int player_num
        }
    }
    render(){
        return(
            <div>
                <EmoBar displayed_player={this.state.displayed_player} match_state={this.props.match_state} />
                <SomePlayerMain player={this.props.game_state.players[this.state.displayed_player]}/>
            </div>
        )
    }

}

