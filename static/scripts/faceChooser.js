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
            <div>
                <MdFace className={"utility_button"}/>
            </div>
        )
        this.expanded = (
            <div>
                {Object.values(faces).map(face => (
                    <div key={face.name} onClick={() => (this.props.updateFaceCallback(face.name))}>
                        <span>{face.icon}</span>
                    </div>
                ))}
            </div>
        )
    }
}

export default FaceChooser