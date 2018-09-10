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
            <div>
                {faces.map(some_face => (
                    <image src={some_face.icon}
                           className={"emo_face_profile"} // maybe we'll need a seperate classname for css here
                           onClick={this.props.updateFaceCallback(some_face.name)}/>
                ))}
            </div>
        )
    }
}

export default FaceChooser