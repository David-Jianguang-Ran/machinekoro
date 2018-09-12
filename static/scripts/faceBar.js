import { MdKeyboardArrowLeft , MdKeyboardArrowRight } from "react-icons/md"
import React from "react"

import EmoFace from "./emoFace"
import emojis from "./emojis.json"
import faces from "./faces.json"

class FaceBar extends React.Component{
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
                emoji:emojis[this.props.match_state[key].emoji].icon,
                selected:(key == this.props.displayed_player) // i know about the type coercion, its desired here
            }
            face_list.push(data)
        }
        return(
            <div>
                <MdKeyboardArrowLeft onClick={this.props.setDisplayedPlayerCallback(
                    () =>(this.computeNextPlayerNum(-1))
                )}/>
                {face_list.map(obj =>(
                    <EmoFace key={obj.num}
                             face={obj.face}
                             emoji={obj.emoji}
                             selected={obj.selected}
                    />
                ))}
                <MdKeyboardArrowRight onClick={this.props.setDisplayedPlayerCallback(
                    () =>(this.computeNextPlayerNum(1))
                )}/>
            </div>
        )
    }
}

export default FaceBar