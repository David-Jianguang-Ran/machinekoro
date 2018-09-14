import { MdFace } from "react-icons/md"
import React from "react"


import ExpandableButton from "./expandableButton"
import faces from "./faces"

class FaceChooser extends ExpandableButton{
    /*
    This component

    props:
    updateFaceCallback

    */
    constructor(props){
        super(props)
        this.button = (
            <div className={"utility_button"}>
                <MdFace/>
            </div>
        )
        this.expanded = (
            <ul>
                {Object.values(faces).map(face => (
                    <li key={face.name} onClick={() => (this.props.updateEmojiCallback(face.icon))}>
                        <span>{face.icon}</span>
                    </li>
                ))}
            </ul>
        )
    }
}

export default FaceChooser