import { MdSentimentSatisfied } from "react-icons/md"
import React from "react"


import ExpandableButton from "./expandableButton"
import emojis from "./emojis"

class EmojiChooser extends ExpandableButton{
    /*
    This component

    props:
    updateEmojiCallback

    */
    constructor(props){
        super(props)
        this.button = (
            <div className={"utility_button"}>
                <MdSentimentSatisfied/>
            </div>
        )
        this.expanded = (
            <div>
                {Object.values(emojis).map(emoji => (
                    <div key={emoji.name} onClick={() => (this.props.updateEmojiCallback(emoji.name))}>
                        <span>{emoji.icon}</span>
                    </div>
                ))}
            </div>
        )
    }
}

export default EmojiChooser
