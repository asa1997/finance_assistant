import streamlit as st
import subprocess
import os
import json

st.set_page_config(layout="wide")
st.title("AI Security Filter Bypass Demo")
st.markdown("""
This demo illustrates a critical vulnerability: how a simple text-based security filter
can be bypassed when a malicious command is encoded as audio. This highlights the
need for defenses that understand *intent*, not just exact text strings.
""")

# Determine the project root dynamically
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if st.button("Run Promptfoo Tests"):
    st.info("Running promptfoo tests... This might take a moment as Whisper transcribes audio.")
    
    # Change to the project root directory where promptfooconfig.yaml is located
    original_cwd = os.getcwd()
    os.chdir(project_root)

    try:
        # Run promptfoo and capture output as JSON for easier parsing
        result = subprocess.run(
            ["promptfoo", "redteam", "run", "--config", "promptfooconfig.yaml", "--output", "promptfoo_results.json"],
            capture_output=True,
            text=True,
            check=True # Raise CalledProcessError for non-zero exit codes
        )
        st.success("Promptfoo tests completed!")
        
        # Display results from JSON report
        results_file = "promptfoo_results.json"
        if os.path.exists(results_file):
            with open(results_file, "r") as f:
                results_data = json.load(f)
            
            st.subheader("Promptfoo Test Results Summary")
            
            # Check for overall success
            all_tests_passed = True
            for test_group in results_data.get('results', []):
                for test in test_group.get('tests', []):
                    if not test.get('success', False):
                        all_tests_passed = False
                        break
                if not all_tests_passed:
                    break
            
            if all_tests_passed:
                st.success("All promptfoo tests passed successfully!")
            else:
                st.warning("Some promptfoo tests failed. Review the details below.")

            for test_group in results_data.get('results', []):
                for test in test_group.get('tests', []):
                    description = test.get('description', 'N/A')
                    success = test.get('success', False)
                    output = test.get('output', {}).get('text', 'No output')
                    
                    status_icon = "✅" if success else "❌"
                    st.markdown(f"### {status_icon} {description}")
                    
                    with st.expander(f"View Details for '{description}'"):
                        st.code(output)
                        if not success:
                            st.error(f"Assertions failed: {test.get('assertionResults', 'No details')}")
        else:
            st.error("Could not find promptfoo_results.json. Check promptfoo execution.")

    except subprocess.CalledProcessError as e:
        st.error(f"Promptfoo command failed with exit code {e.returncode}:")
        st.code(e.stderr)
        st.code(e.stdout) # Also show stdout in case of partial success/logs
    except FileNotFoundError:
        st.error("Promptfoo command not found. Is it installed globally (npm install -g promptfoo) and in your PATH?")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    finally:
        os.chdir(original_cwd) # Change back to original directory

st.markdown("---")
st.subheader("How it works:")
st.markdown("""
1.  **FastAPI Backend (AI Assistant):**
    *   **`/text_query`:** Accepts text. Applies a simple string-based filter (e.g., blocks `"transfer funds"`). If allowed, Llama 3 generates a response.
    *   **`/audio_query`:** Accepts an audio file. `faster-whisper` transcribes it to text. The *same* simple string-based filter is applied to the transcription. If allowed, Llama 3 generates a response.
2.  **Promptfoo (Attacker Tool):**
    *   Sends test cases:
        *   Direct text containing "transfer funds" (expected to be **blocked** by the naive filter).
        *   Audio containing "transfer funds" (expected to **BYPASS** the naive filter, as transcription might not be exact, or the filter isn't applied to the raw audio, demonstrating the vulnerability).
        *   Benign text and audio queries (expected to be allowed).
3.  **Streamlit Dashboard:** Orchestrates the `promptfoo` execution and displays the results, clearly showing the bypass.
""")
