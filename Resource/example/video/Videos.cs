using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Video;
using UnityEngine.UI;
using UnityEngine.Networking;

public class Videos : MonoBehaviour
{
    private Camera cam1, cam2; //兩個不同的攝影機
    private Canvas canvas1;
    public Button btn_1, btn_2, btn_3;

    public VideoPlayer movie;
    public GameObject panel;
    private bool movie_b;
    public GameObject cam3;

    // Use this for initialization
    void Start()
    {
        cam1 = GameObject.Find("Main Camera").GetComponent<Camera>();
        cam2 = GameObject.Find("Camera").GetComponent<Camera>();
        canvas1 = GameObject.Find("Canvas").GetComponent<Canvas>();
        btn_1 = GameObject.Find("Replay").GetComponent<Button>();
        btn_2 = GameObject.Find("Pause").GetComponent<Button>();
        btn_3 = GameObject.Find("Back").GetComponent<Button>();
        cam1.gameObject.SetActive(true);
        cam2.gameObject.SetActive(false);
        btn_1.onClick.AddListener(Replay);
        btn_2.onClick.AddListener(pause);
        btn_3.onClick.AddListener(backtestgame);
        movie.playOnAwake = false;
        movie.loopPointReached += EndReached;
    }

    void Update()
    {
        if (Input.GetKey("z") == true)
        {
            //若是按下鍵盤的z則切換成第二部攝影機
            cam1.gameObject.SetActive(false);
            cam2.gameObject.SetActive(true);
        }
        else if (Input.GetKey("x") == true)
        {
            //若是按下鍵盤的x則切換成第一部攝影機
            cam2.gameObject.SetActive(false);
            cam1.gameObject.SetActive(true);
        }
        if (movie.isPlaying)
        {
            panel.SetActive(false);

        }
        else
        {
            panel.SetActive(true);
        }
        if (movie.isPrepared && !movie_b)
        {
            VideoPlayer videoPlayer = GetComponent<VideoPlayer>();
            Texture vidTex = videoPlayer.texture;
            float videoWidth = vidTex.width;
            float videoHeight = vidTex.height;
        }
    }
    public void playmovie()
    {
        canvas1.gameObject.SetActive(false);
        cam1.gameObject.SetActive(false);
        cam2.gameObject.SetActive(true);
        movie.Stop();
        movie.Play();
        cam1.gameObject.SetActive(false);
        cam2.gameObject.SetActive(true);
        /*cam1.depth = 2;
		cam1.depth = 1;*/
        if (cam3.activeSelf)
        {
            cam3.SetActive(false);
        }
        panel.SetActive(false);
    }
    public void backtestgame()
    {
        btn_2.gameObject.SetActive(true);
        canvas1.gameObject.SetActive(true);
        movie.Stop();
        cam2.gameObject.SetActive(false);
        cam1.gameObject.SetActive(true);
        cam1.depth = 1;
        cam1.depth = 2;
    }
    public void Replay()
    {
        if ((int)(movie.time) > 1 || !movie.isPlaying)
        {
            btn_2.gameObject.SetActive(true);
            movie.Stop();
            movie.Play();
        }
    }
    public void pause()
    {
        if (movie.isPlaying)
        {
            movie.Pause();
        }
        else
        {
            movie.Play();
        }
    }
    void EndReached(UnityEngine.Video.VideoPlayer videoPlayer)
    {
        btn_2.gameObject.SetActive(false);

    }
}
