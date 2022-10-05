resource "helm_release" "niclas-rest-api" {

  name = "niclas-rest-api"

  repository = "../"
  chart      = "k8s"
  namespace  = "default"

    depends_on = [
    helm_release.my-kube-prometheus-stack
  ]

}


resource "helm_release" "my-kube-prometheus-stack" {

  name = "my-kube-prometheus-stack"

  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = "default"
}