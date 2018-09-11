import { MdKeyboardArrowLeft , MdKeyboardArrowRight } from "react-icons/md"
import React from "react"

import EmoFace from "./emoFace"
import emojis from "./emojis.json"
import faces from "./faces.json"

class EmoBar extends React.Component{
    /*
    This component also has the controls needed to cycle through the carousel
    props:
        - displayed_player
        - match_state
        - setDisplayedPlayerCallback(player_num)
    */
    computeNextPlayerNum(shift_count){
        let player_count = this.props.match_state.length()
        return (this.props.displayed_player + player_count + shift_count ) % player_count
    }
    render(){
        // prepare a list of face data obj
        let face_list = []
        for (let key in this.props.match_state){
            let data = {
                num:key,
                face:faces[this.props.match_state[key].face].icon,
                emoji:emojis[this.props.match_state[key].emoji].icon
            }
            face_list.push(data)
        }
        return(
            <div>
                <MdKeyboardArrowLeft onClick={this.props.setDisplayedPlayerCallback(this.computeNextPlayerNum(-1))}/>
                {face_list.map(obj =>(
                    <EmoFace key={obj.num} face={obj.face} emoji={obj.emoji}/>
                ))}
                <MdKeyboardArrowRight onClick={this.props.setDisplayedPlayerCallback(this.computeNextPlayerNum(1))}/>
            </div>
        )
    }
}