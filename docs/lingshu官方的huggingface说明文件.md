---
license: mit
library_name: transformers
pipeline_tag: image-text-to-text
tags:
- medical
- multimodal
- report generation
- radiology
- clinical-reasoning
- MRI
- CT
- Histopathology
- X-ray
- Fundus
---

<p align="center">
  <img src="lingshu_logo.png" width="200" />
</p>
<p align="center">
<a href="https://alibaba-damo-academy.github.io/lingshu/" target="_blank" rel="noopener">Website</a>
&nbsp;&nbsp;
<a href="https://huggingface.co/lingshu-medical-mllm/Lingshu-7B" target="_blank" rel="noopener"> 🤖 7B Model</a>
&nbsp;&nbsp;
<a href="https://huggingface.co/lingshu-medical-mllm/Lingshu-32B" target="_blank" rel="noopener"> 🤖 32B Model</a>
&nbsp;&nbsp;
<a href="https://github.com/alibaba-damo-academy/MedEvalKit" target="_blank" rel="noopener"> MedEvalKit </a>
&nbsp;&nbsp;
<a href="https://arxiv.org/abs/2506.07044" target="_blank" rel="noopener">Technical Report</a>
&nbsp;&nbsp;
<a href="https://github.com/alibaba-damo-academy/Lingshu_MCP" target="_blank" rel="noopener">Lingshu MCP</a>
</p>

# *Lingshu* - SOTA Multimodal Large Language Models for Medical Domain


# <strong style="color: red">BIG NEWS: <a href="https://huggingface.co/lingshu-medical-mllm/Lingshu-7B">Lingshu</a> is released with state-of-the-art performance on medical VQA tasks and report generation.</strong>
This repository contains the model of the paper [Lingshu: A Generalist Foundation Model for Unified Multimodal Medical Understanding and Reasoning](https://huggingface.co/papers/2506.07044). We also release a comprehensive medical evaluation toolkit in [MedEvalKit](https://github.com/alibaba-damo-academy/MedEvalKit), which supports fast evaluation of major multimodal and textual medical tasks.

<p align="center">
  <img src="lingshu_overview_rev.png" width="1500" />
</p>


### Highlights
* [Lingshu](https://huggingface.co/lingshu-medical-mllm/Lingshu-7B) models achieve SOTA on most medical multimodal/textual QA and report generation tasks for 7B and 32 model sizes.
* [Lingshu-32B](https://huggingface.co/lingshu-medical-mllm/Lingshu-32B) outperforms GPT-4.1 and Claude Sonnet 4 in most multimodal QA and report generation tasks.
* Lingshu supports more than 12 medical imaging modalities, including X-Ray, CT Scan, MRI, Microscopy, Ultrasound, Histopathology, Dermoscopy, Fundus, OCT, Digital Photography, Endoscopy, and PET.

### Release
- Technical report: [Arxiv: Lingshu: A Generalist Foundation Model for Unified Multimodal Medical Understanding and Reasoning](https://arxiv.org/pdf/2506.07044).
- Model weights:
  - [Lingshu-7B](https://huggingface.co/lingshu-medical-mllm/Lingshu-7B)
  - [Lingshu-32B](https://huggingface.co/lingshu-medical-mllm/Lingshu-32B)


> **Disclaimer**:
> We must note that even though the weights, codes, and demos are released in an open manner, similar to other pre-trained language models, and despite our best efforts in red teaming and safety fine-tuning and enforcement, our models come with potential risks, including but not limited to inaccurate, misleading or potentially harmful generation.
> Developers and stakeholders should perform their own red teaming and provide related security measures before deployment, and they must abide by and comply with local governance and regulations.
> In no event shall the authors be held liable for any claim, damages, or other liability arising from the use of the released weights, codes, or demos.


## Evaluation


### Medical Multimodal VQA



<table>
  <thead>
    <tr>
      <th>Models</th>
      <th>MMMU-Med</th>
      <th>VQA-RAD</th>
      <th>SLAKE</th>
      <th>PathVQA</th>
      <th>PMC-VQA</th>
      <th>OmniMedVQA</th>
      <th>MedXpertQA</th>
      <th>Avg.</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="9" style="text-align:center;"><strong>Proprietary Models</strong></td>
    </tr>
    <tr>
      <td>GPT-4.1</td>
      <td>75.2</td>
      <td>65.0</td>
      <td>72.2</td>
      <td>55.5</td>
      <td>55.2</td>
      <td>75.5</td>
      <td>45.2</td>
      <td>63.4</td>
    </tr>
    <tr>
      <td>Claude Sonnet 4</td>
      <td>74.6</td>
      <td>67.6</td>
      <td>70.6</td>
      <td>54.2</td>
      <td>54.4</td>
      <td>65.5</td>
      <td>43.3</td>
      <td>61.5</td>
    </tr>
    <tr>
      <td>Gemini-2.5-Flash</td>
      <td>76.9</td>
      <td>68.5</td>
      <td>75.8</td>
      <td>55.4</td>
      <td>55.4</td>
      <td>71.0</td>
      <td>52.8</td>
      <td>65.1</td>
    </tr>
    <tr>
      <td colspan="9" style="text-align:center;"><strong>Open-source Models (&lt;10B)</strong></td>
    </tr>
    <tr>
      <td>BiomedGPT</td>
      <td>24.9</td>
      <td>16.6</td>
      <td>13.6</td>
      <td>11.3</td>
      <td>27.6</td>
      <td>27.9</td>
      <td>-</td>
      <td>-</td>
    </tr>
    <tr>
      <td>Med-R1-2B</td>
      <td>34.8</td>
      <td>39.0</td>
      <td>54.5</td>
      <td>15.3</td>
      <td>47.4</td>
      <td>-</td>
      <td>21.1</td>
      <td>-</td>
    </tr>
    <tr>
      <td>MedVLM-R1-2B</td>
      <td>35.2</td>
      <td>48.6</td>
      <td>56.0</td>
      <td>32.5</td>
      <td>47.6</td>
      <td>77.7</td>
      <td>20.4</td>
      <td>45.4</td>
    </tr>
    <tr>
      <td>MedGemma-4B-IT</td>
      <td>43.7</td>
      <td><strong><u>72.5</u></strong></td>
      <td><u>76.4</u></td>
      <td><u>48.8</u></td>
      <td>49.9</td>
      <td>69.8</td>
      <td>22.3</td>
      <td>54.8</td>
    </tr>
    <tr>
      <td>LLaVA-Med-7B</td>
      <td>29.3</td>
      <td>53.7</td>
      <td>48.0</td>
      <td>38.8</td>
      <td>30.5</td>
      <td>44.3</td>
      <td>20.3</td>
      <td>37.8</td>
    </tr>
    <tr>
      <td>HuatuoGPT-V-7B</td>
      <td>47.3</td>
      <td>67.0</td>
      <td>67.8</td>
      <td>48.0</td>
      <td>53.3</td>
      <td>74.2</td>
      <td>21.6</td>
      <td>54.2</td>
    </tr>
    <tr>
      <td>BioMediX2-8B</td>
      <td>39.8</td>
      <td>49.2</td>
      <td>57.7</td>
      <td>37.0</td>
      <td>43.5</td>
      <td>63.3</td>
      <td>21.8</td>
      <td>44.6</td>
    </tr>
    <tr>
      <td>Qwen2.5VL-7B</td>
      <td>50.6</td>
      <td>64.5</td>
      <td>67.2</td>
      <td>44.1</td>
      <td>51.9</td>
      <td>63.6</td>
      <td>22.3</td>
      <td>52.0</td>
    </tr>
    <tr>
      <td>InternVL2.5-8B</td>
      <td>53.5</td>
      <td>59.4</td>
      <td>69.0</td>
      <td>42.1</td>
      <td>51.3</td>
      <td><u>81.3</u></td>
      <td>21.7</td>
      <td>54.0</td>
    </tr>
    <tr>
      <td>InternVL3-8B</td>
      <td><strong>59.2</strong></td>
      <td>65.4</td>
      <td>72.8</td>
      <td>48.6</td>
      <td><u>53.8</u></td>
      <td>79.1</td>
      <td><u>22.4</u></td>
      <td><u>57.3</u></td>
    </tr>
    <tr>
      <td><strong>Lingshu-7B</strong></td>
      <td><u>54.0</u></td>
      <td><u>67.9</u></td>
      <td><strong>83.1</strong></td>
      <td><strong>61.9</strong></td>
      <td><strong>56.3</strong></td>
      <td><strong>82.9</strong></td>
      <td><strong>26.7</strong></td>
      <td><strong>61.8</strong></td>
    </tr>
    <tr>
      <td colspan="9" style="text-align:center;"><strong>Open-source Models (&gt;10B)</strong></td>
    </tr>
    <tr>
      <td>HealthGPT-14B</td>
      <td>49.6</td>
      <td>65.0</td>
      <td>66.1</td>
      <td><u>56.7</u></td>
      <td>56.4</td>
      <td>75.2</td>
      <td>24.7</td>
      <td>56.2</td>
    </tr>
    <tr>
      <td>HuatuoGPT-V-34B</td>
      <td>51.8</td>
      <td>61.4</td>
      <td>69.5</td>
      <td>44.4</td>
      <td>56.6</td>
      <td>74.0</td>
      <td>22.1</td>
      <td>54.3</td>
    </tr>
    <tr>
      <td>MedDr-40B</td>
      <td>49.3</td>
      <td>65.2</td>
      <td>66.4</td>
      <td>53.5</td>
      <td>13.9</td>
      <td>64.3</td>
      <td>-</td>
      <td>-</td>
    </tr>
    <tr>
      <td>InternVL3-14B</td>
      <td><u>63.1</u></td>
      <td>66.3</td>
      <td><u>72.8</u></td>
      <td>48.0</td>
      <td>54.1</td>
      <td>78.9</td>
      <td>23.1</td>
      <td>58.0</td>
    </tr>
    <tr>
      <td>Qwen2.5V-32B</td>
      <td>59.6</td>
      <td><u>71.8</u></td>
      <td>71.2</td>
      <td>41.9</td>
      <td>54.5</td>
      <td>68.2</td>
      <td>25.2</td>
      <td>56.1</td>
    </tr>
    <tr>
      <td>InternVL2.5-38B</td>
      <td>61.6</td>
      <td>61.4</td>
      <td>70.3</td>
      <td>46.9</td>
      <td><u>57.2</u></td>
      <td><u>79.9</u></td>
      <td>24.4</td>
      <td>57.4</td>
    </tr>
    <tr>
      <td>InternVL3-38B</td>
      <td><strong>65.2</strong></td>
      <td>65.4</td>
      <td>72.7</td>
      <td>51.0</td>
      <td>56.6</td>
      <td>79.8</td>
      <td><u>25.2</u></td>
      <td><u>59.4</u></td>
    </tr>
    <tr>
      <td><strong>Lingshu-32B</strong></td>
      <td>62.3</td>
      <td><strong>76.5</strong></td>
      <td><strong>89.2</strong></td>
      <td><strong>65.9</strong></td>
      <td><strong>57.9</strong></td>
      <td><strong>83.4</strong></td>
      <td><strong>30.9</strong></td>
      <td><strong>66.6</strong></td>
    </tr>
  </tbody>
</table>


### Medical Textual QA

<table>
  <thead>
    <tr>
      <th>Models</th>
      <th>MMLU-Med</th>
      <th>PubMedQA</th>
      <th>MedMCQA</th>
      <th>MedQA</th>
      <th>Medbullets</th>
      <th>MedXpertQA</th>
      <th>SuperGPQA-Med</th>
      <th>Avg.</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="9" style="text-align:center;"><strong>Proprietary Models</strong></td>
    </tr>
    <tr>
      <td>GPT-4.1</td>
      <td>89.6</td>
      <td>75.6</td>
      <td>77.7</td>
      <td>89.1</td>
      <td>77.0</td>
      <td>30.9</td>
      <td>49.9</td>
      <td>70.0</td>
    </tr>
    <tr>
      <td>Claude Sonnet 4</td>
      <td>91.3</td>
      <td>78.6</td>
      <td>79.3</td>
      <td>92.1</td>
      <td>80.2</td>
      <td>33.6</td>
      <td>56.3</td>
      <td>73.1</td>
    </tr>
    <tr>
      <td>Gemini-2.5-Flash</td>
      <td>84.2</td>
      <td>73.8</td>
      <td>73.6</td>
      <td>91.2</td>
      <td>77.6</td>
      <td>35.6</td>
      <td>53.3</td>
      <td>69.9</td>
    </tr>
    <tr>
      <td colspan="9" style="text-align:center;"><strong>Open-source Models (&lt;10B)</strong></td>
    </tr>
    <tr>
      <td>Med-R1-2B</td>
      <td>51.5</td>
      <td>66.2</td>
      <td>39.1</td>
      <td>39.9</td>
      <td>33.6</td>
      <td>11.2</td>
      <td>17.9</td>
      <td>37.0</td>
    </tr>
    <tr>
      <td>MedVLM-R1-2B</td>
      <td>51.8</td>
      <td>66.4</td>
      <td>39.7</td>
      <td>42.3</td>
      <td>33.8</td>
      <td>11.8</td>
      <td>19.1</td>
      <td>37.8</td>
    </tr>
    <tr>
      <td>MedGemma-4B-IT</td>
      <td>66.7</td>
      <td>72.2</td>
      <td>52.2</td>
      <td>56.2</td>
      <td>45.6</td>
      <td>12.8</td>
      <td>21.6</td>
      <td>46.8</td>
    </tr>
    <tr>
      <td>LLaVA-Med-7B</td>
      <td>50.6</td>
      <td>26.4</td>
      <td>39.4</td>
      <td>42.0</td>
      <td>34.4</td>
      <td>9.9</td>
      <td>16.1</td>
      <td>31.3</td>
    </tr>
    <tr>
      <td>HuatuoGPT-V-7B</td>
      <td>69.3</td>
      <td>72.8</td>
      <td>51.2</td>
      <td>52.9</td>
      <td>40.9</td>
      <td>10.1</td>
      <td>21.9</td>
      <td>45.6</td>
    </tr>
    <tr>
      <td>BioMediX2-8B</td>
      <td>68.6</td>
      <td>75.2</td>
      <td>52.9</td>
      <td>58.9</td>
      <td>45.9</td>
      <td>13.4</td>
      <td>25.2</td>
      <td>48.6</td>
    </tr>
    <tr>
      <td>Qwen2.5VL-7B</td>
      <td>73.4</td>
      <td><u>76.4</u></td>
      <td>52.6</td>
      <td>57.3</td>
      <td>42.1</td>
      <td>12.8</td>
      <td>26.3</td>
      <td>48.7</td>
    </tr>
    <tr>
      <td>InternVL2.5-8B</td>
      <td>74.2</td>
      <td>76.4</td>
      <td>52.4</td>
      <td>53.7</td>
      <td>42.4</td>
      <td>11.6</td>
      <td>26.1</td>
      <td>48.1</td>
    </tr>
    <tr>
      <td>InternVL3-8B</td>
      <td><strong>77.5</strong></td>
      <td>75.4</td>
      <td><strong>57.7</strong></td>
      <td><u>62.1</u></td>
      <td><u>48.5</u></td>
      <td><u>13.1</u></td>
      <td><strong>31.2</strong></td>
      <td><u>52.2</u></td>
    </tr>
    <tr>
      <td><strong>Lingshu-7B</strong></td>
      <td><u>74.5</u></td>
      <td><strong>76.6</strong></td>
      <td><u>55.9</u></td>
      <td><strong>63.3</strong></td>
      <td><strong>56.2</strong></td>
      <td><strong>16.5</strong></td>
      <td><u>26.3</u></td>
      <td><strong>52.8</strong></td>
    </tr>
    <tr>
      <td colspan="9" style="text-align:center;"><strong>Open-source Models (&gt;10B)</strong></td>
    </tr>
    <tr>
      <td>HealthGPT-14B</td>
      <td>80.2</td>
      <td>68.0</td>
      <td>63.4</td>
      <td>66.2</td>
      <td>39.8</td>
      <td>11.3</td>
      <td>25.7</td>
      <td>50.7</td>
    </tr>
    <tr>
      <td>HuatuoGPT-V-34B</td>
      <td>74.7</td>
      <td>72.2</td>
      <td>54.7</td>
      <td>58.8</td>
      <td>42.7</td>
      <td>11.4</td>
      <td>26.5</td>
      <td>48.7</td>
    </tr>
    <tr>
      <td>MedDr-40B</td>
      <td>65.2</td>
      <td>77.4</td>
      <td>38.4</td>
      <td>59.2</td>
      <td>44.3</td>
      <td>12.0</td>
      <td>24.0</td>
      <td>45.8</td>
    </tr>
    <tr>
      <td>InternVL3-14B</td>
      <td>81.7</td>
      <td><u>77.2</u></td>
      <td>62.0</td>
      <td>70.1</td>
      <td>49.5</td>
      <td>14.1</td>
      <td>37.9</td>
      <td>56.1</td>
    </tr>
    <tr>
      <td>Qwen2.5VL-32B</td>
      <td>83.2</td>
      <td>68.4</td>
      <td>63.0</td>
      <td>71.6</td>
      <td>54.2</td>
      <td>15.6</td>
      <td>37.6</td>
      <td>56.2</td>
    </tr>
    <tr>
      <td>InternVL2.5-38B</td>
      <td><u>84.6</u></td>
      <td>74.2</td>
      <td><u>65.9</u></td>
      <td><u>74.4</u></td>
      <td><u>55.0</u></td>
      <td>14.7</td>
      <td>39.9</td>
      <td>58.4</td>
    </tr>
    <tr>
      <td>InternVL3-38B</td>
      <td>83.8</td>
      <td>73.2</td>
      <td>64.9</td>
      <td>73.5</td>
      <td>54.6</td>
      <td><u>16.0</u></td>
      <td><strong>42.5</strong></td>
      <td><u>58.4</u></td>
    </tr>
    <tr>
      <td><strong>Lingshu-32B</strong></td>
      <td><strong>84.7</strong></td>
      <td><strong>77.8</strong></td>
      <td><strong>66.1</strong></td>
      <td><strong>74.7</strong></td>
      <td><strong>65.4</strong></td>
      <td><strong>22.7</strong></td>
      <td><u>41.1</u></td>
      <td><strong>61.8</strong></td>
    </tr>
  </tbody>
</table>


####  Medical Report Generation


<table>
  <thead>
    <tr>
      <th rowspan="3">Models</th>
      <th colspan="5">MIMIC-CXR</th>
      <th colspan="5">CheXpert Plus</th>
      <th colspan="5">IU-Xray</th>
    </tr>
    <tr>
      <th>ROUGE-L</th>
      <th>CIDEr</th>
      <th>RaTE</th>
      <th>SembScore</th>
      <th>RadCliQ-v1<sup>-1</sup></th>
      <th>ROUGE-L</th>
      <th>CIDEr</th>
      <th>RaTE</th>
      <th>SembScore</th>
      <th>RadCliQ-v1<sup>-1</sup></th>
      <th>ROUGE-L</th>
      <th>CIDEr</th>
      <th>RaTE</th>
      <th>SembScore</th>
      <th>RadCliQ-v1<sup>-1</sup></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="16" style="text-align:center;"><strong>Proprietary Models</strong></td>
    </tr>
    <tr>
      <td>GPT-4.1</td>
      <td>9.0</td>
      <td>82.8</td>
      <td>51.3</td>
      <td>23.9</td>
      <td>57.1</td>
      <td>24.5</td>
      <td>78.8</td>
      <td>45.5</td>
      <td>23.2</td>
      <td>45.5</td>
      <td>30.2</td>
      <td>124.6</td>
      <td>51.3</td>
      <td>47.5</td>
      <td>80.3</td>
    </tr>
    <tr>
      <td>Claude Sonnet 4</td>
      <td>20.0</td>
      <td>56.6</td>
      <td>45.6</td>
      <td>19.7</td>
      <td>53.4</td>
      <td>22.0</td>
      <td>59.5</td>
      <td>43.5</td>
      <td>18.9</td>
      <td>43.3</td>
      <td>25.4</td>
      <td>88.3</td>
      <td>55.4</td>
      <td>41.0</td>
      <td>72.1</td>
    </tr>
    <tr>
      <td>Gemini-2.5-Flash</td>
      <td>25.4</td>
      <td>80.7</td>
      <td>50.3</td>
      <td>29.7</td>
      <td>59.4</td>
      <td>23.6</td>
      <td>72.2</td>
      <td>44.3</td>
      <td>27.4</td>
      <td>44.0</td>
      <td>33.5</td>
      <td>129.3</td>
      <td>55.6</td>
      <td>50.9</td>
      <td>91.6</td>
    </tr>
    <tr>
      <td colspan="16" style="text-align:center;"><strong>Open-source Models (&lt;10B)</strong></td>
    </tr>
    <tr>
      <td>Med-R1-2B</td>
      <td>19.3</td>
      <td>35.4</td>
      <td>40.6</td>
      <td>14.8</td>
      <td>42.4</td>
      <td>18.6</td>
      <td>37.1</td>
      <td>38.5</td>
      <td>17.8</td>
      <td>37.6</td>
      <td>16.1</td>
      <td>38.3</td>
      <td>41.4</td>
      <td>12.5</td>
      <td>43.6</td>
    </tr>
    <tr>
      <td>MedVLM-R1-2B</td>
      <td>20.3</td>
      <td>40.1</td>
      <td>41.6</td>
      <td>14.2</td>
      <td>48.3</td>
      <td>20.9</td>
      <td>43.5</td>
      <td>38.9</td>
      <td>15.5</td>
      <td>40.9</td>
      <td>22.7</td>
      <td>61.1</td>
      <td>46.1</td>
      <td>22.7</td>
      <td>54.3</td>
    </tr>
    <tr>
      <td>MedGemma-4B-IT</td>
      <td><u>25.6</u></td>
      <td><u>81.0</u></td>
      <td><strong>52.4</strong></td>
      <td><u>29.2</u></td>
      <td><u>62.9</u></td>
      <td><strong>27.1</strong></td>
      <td><u>79.0</u></td>
      <td><strong>47.2</strong></td>
      <td><strong>29.3</strong></td>
      <td><u>46.6</u></td>
      <td><u>30.8</u></td>
      <td>103.6</td>
      <td><u>57.0</u></td>
      <td><u>46.8</u></td>
      <td><u>86.7</u></td>
    </tr>
    <tr>
      <td>LLaVA-Med-7B</td>
      <td>15.0</td>
      <td>43.4</td>
      <td>12.8</td>
      <td>18.3</td>
      <td>52.9</td>
      <td>18.4</td>
      <td>45.5</td>
      <td>38.8</td>
      <td>23.5</td>
      <td>44.0</td>
      <td>18.8</td>
      <td>68.2</td>
      <td>40.9</td>
      <td>16.0</td>
      <td>58.1</td>
    </tr>
    <tr>
      <td>HuatuoGPT-V-7B</td>
      <td>23.4</td>
      <td>69.5</td>
      <td>48.9</td>
      <td>20.0</td>
      <td>48.2</td>
      <td>21.3</td>
      <td>64.7</td>
      <td>44.2</td>
      <td>19.3</td>
      <td>39.4</td>
      <td>29.6</td>
      <td><u>104.3</u></td>
      <td>52.9</td>
      <td>40.7</td>
      <td>63.6</td>
    </tr>
    <tr>
      <td>BioMediX2-8B</td>
      <td>20.0</td>
      <td>52.8</td>
      <td>44.4</td>
      <td>17.7</td>
      <td>53.0</td>
      <td>18.1</td>
      <td>47.9</td>
      <td>40.8</td>
      <td>21.6</td>
      <td>43.3</td>
      <td>19.6</td>
      <td>58.8</td>
      <td>40.1</td>
      <td>11.6</td>
      <td>53.8</td>
    </tr>
    <tr>
      <td>Qwen2.5VL-7B</td>
      <td>24.1</td>
      <td>63.7</td>
      <td>47.0</td>
      <td>18.4</td>
      <td>55.1</td>
      <td>22.2</td>
      <td>62.0</td>
      <td>41.0</td>
      <td>17.2</td>
      <td>43.1</td>
      <td>26.5</td>
      <td>78.1</td>
      <td>48.4</td>
      <td>36.3</td>
      <td>66.1</td>
    </tr>
    <tr>
      <td>InternVL2.5-8B</td>
      <td>23.2</td>
      <td>61.8</td>
      <td>47.0</td>
      <td>21.0</td>
      <td>56.2</td>
      <td>20.6</td>
      <td>58.5</td>
      <td>43.1</td>
      <td>19.7</td>
      <td>42.7</td>
      <td>24.8</td>
      <td>75.4</td>
      <td>51.1</td>
      <td>36.7</td>
      <td>67.0</td>
    </tr>
    <tr>
      <td>InternVL3-8B</td>
      <td>22.9</td>
      <td>66.2</td>
      <td>48.2</td>
      <td>21.5</td>
      <td>55.1</td>
      <td>20.9</td>
      <td>65.4</td>
      <td>44.3</td>
      <td>25.2</td>
      <td>43.7</td>
      <td>22.9</td>
      <td>76.2</td>
      <td>51.2</td>
      <td>31.3</td>
      <td>59.9</td>
    </tr>
    <tr>
      <td><strong>Lingshu-7B</strong></td>
      <td><strong>30.8</strong></td>
      <td><strong>109.4</strong></td>
      <td><u>52.1</u></td>
      <td><strong>30.0</strong></td>
      <td><strong>69.2</strong></td>
      <td><u>26.5</u></td>
      <td><strong>79.0</strong></td>
      <td><u>45.4</u></td>
      <td><u>26.8</u></td>
      <td><strong>47.3</strong></td>
      <td><strong>41.2</strong></td>
      <td><strong>180.7</strong></td>
      <td><strong>57.6</strong></td>
      <td><strong>48.4</strong></td>
      <td><strong>108.1</strong></td>
    </tr>
    <tr>
      <td colspan="16" style="text-align:center;"><strong>Open-source Models (&gt;10B)</strong></td>
    </tr>
    <tr>
      <td>HealthGPT-14B</td>
      <td>21.4</td>
      <td>64.7</td>
      <td>48.4</td>
      <td>16.5</td>
      <td>52.7</td>
      <td>20.6</td>
      <td><u>66.2</u></td>
      <td><u>44.4</u></td>
      <td>22.7</td>
      <td>42.6</td>
      <td>22.9</td>
      <td>81.9</td>
      <td>50.8</td>
      <td>16.6</td>
      <td>56.9</td>
    </tr>
    <tr>
      <td>HuatuoGPT-V-34B</td>
      <td><u>23.5</u></td>
      <td><u>68.5</u></td>
      <td>48.5</td>
      <td><u>23.0</u></td>
      <td>47.1</td>
      <td>22.5</td>
      <td>62.8</td>
      <td>42.9</td>
      <td>22.1</td>
      <td>39.7</td>
      <td>28.2</td>
      <td><u>108.3</u></td>
      <td>54.4</td>
      <td><u>42.2</u></td>
      <td>59.3</td>
    </tr>
    <tr>
      <td>MedDr-40B</td>
      <td>15.7</td>
      <td>62.3</td>
      <td>45.2</td>
      <td>12.2</td>
      <td>47.0</td>
      <td><u>24.1</u></td>
      <td>66.1</td>
      <td><strong>44.7</strong></td>
      <td><u>24.2</u></td>
      <td>44.7</td>
      <td>19.4</td>
      <td>62.9</td>
      <td>40.3</td>
      <td>7.3</td>
      <td>48.9</td>
    </tr>
    <tr>
      <td>InternVL3-14B</td>
      <td>22.0</td>
      <td>63.7</td>
      <td><u>48.6</u></td>
      <td>17.4</td>
      <td>46.5</td>
      <td>20.4</td>
      <td>60.2</td>
      <td>44.1</td>
      <td>20.7</td>
      <td>39.4</td>
      <td>24.8</td>
      <td>93.7</td>
      <td><u>55.0</u></td>
      <td>38.7</td>
      <td>55.0</td>
    </tr>
    <tr>
      <td>Qwen2.5VL-32B</td>
      <td>15.7</td>
      <td>50.2</td>
      <td>47.5</td>
      <td>17.1</td>
      <td>45.2</td>
      <td>15.2</td>
      <td>54.8</td>
      <td>43.4</td>
      <td>18.5</td>
      <td>40.3</td>
      <td>18.9</td>
      <td>73.3</td>
      <td>51.3</td>
      <td>38.1</td>
      <td>54.0</td>
    </tr>
    <tr>
      <td>InternVL2.5-38B</td>
      <td>22.7</td>
      <td>61.4</td>
      <td>47.5</td>
      <td>18.2</td>
      <td><u>54.9</u></td>
      <td>21.6</td>
      <td>60.6</td>
      <td>42.6</td>
      <td>20.3</td>
      <td><u>45.4</u></td>
      <td><u>28.9</u></td>
      <td>96.5</td>
      <td>53.5</td>
      <td>38.5</td>
      <td><u>69.7</u></td>
    </tr>
    <tr>
      <td>InternVL3-38B</td>
      <td>22.8</td>
      <td>64.6</td>
      <td>47.9</td>
      <td>18.1</td>
      <td>47.2</td>
      <td>20.5</td>
      <td>62.7</td>
      <td>43.8</td>
      <td>20.2</td>
      <td>39.4</td>
      <td>25.5</td>
      <td>90.7</td>
      <td>53.5</td>
      <td>33.1</td>
      <td>55.2</td>
    </tr>
    <tr>
      <td><strong>Lingshu-32B</strong></td>
      <td><strong>28.8</strong></td>
      <td><strong>96.4</strong></td>
      <td><strong>50.8</strong></td>
      <td><strong>30.1</strong></td>
      <td><strong>67.1</strong></td>
      <td><strong>25.3</strong></td>
      <td><strong>75.9</strong></td>
      <td>43.4</td>
      <td><strong>24.2</strong></td>
      <td><strong>47.1</strong></td>
      <td><strong>42.8</strong></td>
      <td><strong>189.2</strong></td>
      <td><strong>63.5</strong></td>
      <td><strong>54.6</strong></td>
      <td><strong>130.4</strong></td>
    </tr>
  </tbody>
</table>



### Usage

#### Using transformers (version 4.52.1 is recommended)
```python
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info


# We recommend enabling flash_attention_2 for better acceleration and memory saving, especially in multi-image and video scenarios.
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "lingshu-medical-mllm/Lingshu-7B",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto",
)

processor = AutoProcessor.from_pretrained("lingshu-medical-mllm/Lingshu-7B")

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": "example.png",
            },
            {"type": "text", "text": "Describe this image."},
        ],
    }
]

# Preparation for inference
text = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
image_inputs, video_inputs = process_vision_info(messages)
inputs = processor(
    text=[text],
    images=image_inputs,
    videos=video_inputs,
    padding=True,
    return_tensors="pt",
)
inputs = inputs.to(model.device)

# Inference: Generation of the output
generated_ids = model.generate(**inputs, max_new_tokens=128)
generated_ids_trimmed = [
    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text = processor.batch_decode(
    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
)
print(output_text)
```


#### Using vLLM
```python
from vllm import LLM, SamplingParams
from qwen_vl_utils import process_vision_info
import PIL
from transformers import AutoProcessor

processor = AutoProcessor.from_pretrained("lingshu-medical-mllm/Lingshu-7B")
llm = LLM(model="lingshu-medical-mllm/Lingshu-7B", limit_mm_per_prompt = {"image": 4}, tensor_parallel_size=2, enforce_eager=True, trust_remote_code=True,)
sampling_params = SamplingParams(
            temperature=0.7,
            top_p=1,
            repetition_penalty=1,
            max_tokens=1024,
            stop_token_ids=[],
        )

text = "What does the image show?"
image_path = "example.png"
image = PIL.Image.open(image_path)

message = [
    {
        "role":"user",
        "content":[
            {"type":"image","image":image},
            {"type":"text","text":text}
            ]
            }
]
prompt = processor.apply_chat_template(
    message,
    tokenize=False,
    add_generation_prompt=True,
)
image_inputs, video_inputs = process_vision_info(message)
mm_data = {}
mm_data["image"] = image_inputs
processed_input = {
  "prompt": prompt,
  "multi_modal_data": mm_data,
}

outputs = llm.generate([processed_input], sampling_params=sampling_params)
print(outputs[0].outputs[0].text)
```


## Citation

If you find our project useful, we hope you would kindly star our repo and cite our work as follows:

```
@article{xu2025lingshu,
  title={Lingshu: A Generalist Foundation Model for Unified Multimodal Medical Understanding and Reasoning},
  author={Xu, Weiwen and Chan, Hou Pong and Li, Long and Aljunied, Mahani and Yuan, Ruifeng and Wang, Jianyu and Xiao, Chenghao and Chen, Guizhen and Liu, Chaoqun and Li, Zhaodonghui and others},
  journal={arXiv preprint arXiv:2506.07044},
  year={2025}
}
```