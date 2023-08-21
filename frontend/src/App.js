import axios from 'axios';
import Button from '@mui/material/Button';
import React, { Component } from 'react';
import Wrapper from './components/Wrapper';
import NavBar from './components/NavBar';

class App extends Component {

	state = {

		// Initially, no file is selected
		selectedFile: null
	};

	// On file select (from the pop up)
	onFileChange = event => {

		// Update the state
		this.setState({ selectedFile: event.target.files[0] });

	};

	// On file upload (click the upload button)
	onFileUpload = () => {

		// Create an object of formData
		const formData = new FormData();

		// Update the formData object
		formData.append(
			"myFile",
			this.state.selectedFile,
			this.state.selectedFile.name
		);

		// Details of the uploaded file
		console.log(this.state.selectedFile);

		// Request made to the backend api
		// Send formData object
		axios.post("api/uploadfile", formData);
	};

	// File content to be displayed after
	// file upload is complete
	fileData = () => {

		if (this.state.selectedFile) {

			return (
				<div>
					<h2>File Details:</h2>
					<p>File Name: {this.state.selectedFile.name}</p>

					<p>File Type: {this.state.selectedFile.type}</p>

					<p>
						Last Modified:{" "}
						{this.state.selectedFile.lastModifiedDate.toDateString()}
					</p>

				</div>
			);
		}
	};



	render() {

    const handleUploadButtonClick = () => {
      document.getElementById('fileInput').click();
    };

		return (
      <div>
      <NavBar></NavBar>
      <Wrapper>
      <div>
      <h1 id="heading">
        3D Pose Estimation
      </h1>
      <h2 id="heading-2">
        Upload an image to get started!
      </h2>
      <div>
        <Button variant="contained" onClick={handleUploadButtonClick}>
          Upload!
        </Button>{' '}
        <input type="file"
                id="fileInput"
                style={{ display: 'none' }}
                onChange={this.onFileChange}>

        </input>
        
        </div>
          {this.fileData()}
        </div>
      </Wrapper>
      </div>
		);
	}
}

export default App;
