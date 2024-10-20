import argparse
from web_module.manage_scraping import (
    scan_web_list,
    add_website,
    delete_web_site,
    delete_web_page
)


def main():
    parser = argparse.ArgumentParser(description="Interface en ligne de commande pour OpaleAI")
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Sous-commande : add_website
    parser_add = subparsers.add_parser('add_website', help='Ajouter un site web à la liste de scraping')
    parser_add.add_argument('url', help='URL du site web à ajouter')
    parser_add.add_argument('--depth', type=int, default=2, help='Profondeur de scraping (par défaut : 2)')
    parser_add.add_argument('--file', default='web_module/website_list.csv', help='Chemin vers le fichier CSV des sites (par défaut : web_module/website_list.csv)')

    # Sous-commande : scan_web_list
    parser_scan = subparsers.add_parser('scan_web_list', help='Scanner la liste des sites web')
    parser_scan.add_argument('--file', default='web_module/website_list.csv', help='Chemin vers le fichier CSV des sites')
    parser_scan.add_argument('--test_mode', action='store_true', help='Exécuter en mode test (pas de scraping réel)')

    # Sous-commande : delete_web_site
    parser_delete_site = subparsers.add_parser('delete_web_site', help='Supprimer un site web de la liste')
    parser_delete_site.add_argument('root_url', help='URL racine du site web à supprimer')
    parser_delete_site.add_argument('--file', default='web_module/website_list.csv', help='Chemin vers le fichier CSV des sites')

    # Sous-commande : delete_web_page
    parser_delete_page = subparsers.add_parser('delete_web_page', help='Supprimer une page web spécifique de la liste')
    parser_delete_page.add_argument('url', help='URL de la page web à supprimer')
    parser_delete_page.add_argument('--file', default='web_module/website_list.csv', help='Chemin vers le fichier CSV des sites')

    args = parser.parse_args()

    if args.command == 'add_website':
        add_website(args.url, args.file, args.depth)
    elif args.command == 'scan_web_list':
        scan_web_list(args.file, test_mode=args.test_mode)
    elif args.command == 'delete_web_site':
        delete_web_site(args.root_url, args.file)
    elif args.command == 'delete_web_page':
        delete_web_page(args.url, args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
